# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import requests

HEADERS = {"Content-Type": "application/sparql-update"}

INSERT_QUERY = """
    INSERT DATA {
        GRAPH <{GRAPH_URI}> {
            {PAYLOAD}
        }
    }
"""


def project_func(sag_endpoint: str, heating_graph_uri: str, data: []):
    query = INSERT_QUERY.replace("{GRAPH_URI}", heating_graph_uri).replace(
        "{PAYLOAD}", "\n".join(data)
    )

    requests.post(sag_endpoint, data=query.encode("utf-8"), headers=HEADERS)
