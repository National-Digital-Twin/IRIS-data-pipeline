#!/usr/bin/env python3
import os
import re
import sys
import time
import signal
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Tuple

from confluent_kafka.admin import AdminClient, OffsetSpec
from confluent_kafka import TopicPartition


USERNAME_PASSWORD_RE = re.compile(r'username="([^"]+)".*password="([^"]+)"')


@dataclass
class ClusterCfg:
    bootstrap_servers: str
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = ""
    sasl_username: str = ""
    sasl_password: str = ""


@dataclass
class RunCfg:
    topics: List[str]
    poll_interval_s: float = 5.0
    no_progress_timeout_s: float = 60.0
    stability_polls_required: int = 3  # require N consecutive "lag==0" polls before success


def parse_properties(path: str) -> Dict[str, str]:
    props: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            props[k.strip()] = v.strip()
    return props


def cluster_from_mm2_props(props: Dict[str, str], alias: str) -> ClusterCfg:
    bs = props.get(f"{alias}.bootstrap.servers", "")
    if not bs:
        raise ValueError(f"Missing {alias}.bootstrap.servers")

    sec = props.get(f"{alias}.security.protocol", "PLAINTEXT")
    mech = props.get(f"{alias}.sasl.mechanism", "")
    jaas = props.get(f"{alias}.sasl.jaas.config", "")

    user = ""
    pwd = ""
    if jaas:
        m = USERNAME_PASSWORD_RE.search(jaas)
        if m:
            user, pwd = m.group(1), m.group(2)

    return ClusterCfg(
        bootstrap_servers=bs,
        security_protocol=sec,
        sasl_mechanism=mech,
        sasl_username=user,
        sasl_password=pwd,
    )


def admin_client(cfg: ClusterCfg) -> AdminClient:
    conf = {
        "bootstrap.servers": cfg.bootstrap_servers,
        "security.protocol": cfg.security_protocol,
    }
    if cfg.security_protocol.startswith("SASL"):
        # librdkafka uses these, not the JAAS string
        conf["sasl.mechanism"] = cfg.sasl_mechanism or "PLAIN"
        conf["sasl.username"] = cfg.sasl_username
        conf["sasl.password"] = cfg.sasl_password
    return AdminClient(conf)


def latest_offset(admin: AdminClient, topic: str, partition: int = 0, timeout_s: float = 10.0) -> int:
    tp = TopicPartition(topic, partition)
    fs = admin.list_offsets({tp: OffsetSpec.latest()})
    fut = fs[tp]
    res = fut.result(timeout=timeout_s)  # returns TopicPartition with .offset
    if res.offset is None or res.offset < 0:
        raise RuntimeError(f"Got invalid latest offset for {topic}-{partition}: {res.offset}")
    return int(res.offset)


def wait_for_brokers(a_admin: AdminClient, b_admin: AdminClient, topics: List[str], max_wait_s: float = 120.0):
    """Best-effort readiness: can we query offsets?"""
    start = time.time()
    while True:
        try:
            for t in topics:
                # If topics don't exist on B yet, MM2 might create them later.
                # So for readiness we just check A topic is queryable.
                _ = latest_offset(a_admin, t)
            return
        except Exception as e:
            if time.time() - start > max_wait_s:
                raise RuntimeError(f"Brokers not ready after {max_wait_s}s: {e}") from e
            time.sleep(2.0)


def terminate_process(proc: subprocess.Popen, grace_s: float = 20.0) -> None:
    if proc.poll() is not None:
        return
    proc.send_signal(signal.SIGTERM)
    deadline = time.time() + grace_s
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.5)
    proc.kill()


def main() -> int:
    mm2_props_path = os.environ.get("MM2_PROPERTIES_PATH", "/etc/mm2.properties")
    cfg = RunCfg(
        topics=[],
        poll_interval_s=float(os.environ.get("POLL_INTERVAL_S", "5")),
        no_progress_timeout_s=float(os.environ.get("NO_PROGRESS_TIMEOUT_S", "60")),
        stability_polls_required=int(os.environ.get("STABILITY_POLLS", "3")),
    )

    props = parse_properties(mm2_props_path)

    topics_raw = props.get("A->B.topics", "")
    if not topics_raw:
        raise ValueError("mm2.properties missing A->B.topics")
    cfg.topics = [t.strip() for t in topics_raw.split(",") if t.strip()]

    a = cluster_from_mm2_props(props, "A")
    b = cluster_from_mm2_props(props, "B")

    a_admin = admin_client(a)
    b_admin = admin_client(b)

    # Wait until A is queryable
    wait_for_brokers(a_admin, b_admin, cfg.topics)

    last_progress_ts = time.time()
    last_b_end: Dict[str, int] = {}
    stable_zero_polls = 0

    while True:

        any_lag = False
        any_progress = False
        all_zero = True

        for topic in cfg.topics:
            a_end = latest_offset(a_admin, topic)
            try:
                b_end = latest_offset(b_admin, topic)
            except Exception:
                # Topic may not exist on B yet; treat as 0 replicated so far
                b_end = 0

            lag = a_end - b_end

            if lag < 0:
                # B ahead of A is unexpected in your flow; treat as error
                return 3

            if lag != 0:
                all_zero = False
                any_lag = True

            prev = last_b_end.get(topic)
            if prev is None or b_end > prev:
                any_progress = True
                last_b_end[topic] = b_end

            print(f"{topic}: A_end={a_end} B_end={b_end} lag={lag}", flush=True)

        now = time.time()
        if any_progress:
            last_progress_ts = now

        if all_zero:
            stable_zero_polls += 1
            # Require both:
            #  - N stable polls
            #  - AND no progress for the timeout window (ensures it really settled)
            if (
                stable_zero_polls >= cfg.stability_polls_required
                and (now - last_progress_ts) >= cfg.no_progress_timeout_s
            ):
                return 0
        else:
            stable_zero_polls = 0
            # If we still have lag, but no progress for too long -> stuck
            if any_lag and (now - last_progress_ts) >= cfg.no_progress_timeout_s:
                return 1

        time.sleep(cfg.poll_interval_s)


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr, flush=True)
        rc = 99
    sys.exit(rc)
