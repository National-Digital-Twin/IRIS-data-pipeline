# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

HEADERS = {"Content-Type": "application/sparql-update"}

INSERT_QUERY = """
    INSERT DATA {
        GRAPH {GRAPH_URI} {
            {PAYLOAD}
        }
    }
"""

RETRY_STRATEGY = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(["HEAD", "OPTIONS", "POST"]),
)


def project_func(sag_endpoint: str, heating_graph_uri: str, data: []):
    query = INSERT_QUERY.replace("{GRAPH_URI}", heating_graph_uri).replace(
        "{PAYLOAD}", "\n".join(data)
    )

    session = requests.Session()

    session.mount("http://", HTTPAdapter(max_retries=RETRY_STRATEGY))
    session.mount("https://", HTTPAdapter(max_retries=RETRY_STRATEGY))

    session.post(sag_endpoint, data=query.encode("utf-8"), headers=HEADERS)
