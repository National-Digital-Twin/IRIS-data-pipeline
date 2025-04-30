# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
 
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import os
import rdflib
import requests
import sys

from dotenv import load_dotenv

load_dotenv()

ttl_file = os.environ.get("TTL_RESTORATION_FILE")
fuseki_url = os.environ.get("FUSEKI_URL")
named_graph = os.environ.get("NAMED_GRAPH_NAME")
chunk_size = 1000

print(f"Loading data from {ttl_file}")
g = rdflib.Graph()
g.parse(ttl_file, format="turtle")

triples = list(g)
total = len(triples)
print(f"Loaded {total} triples.")

def sparql_escape(value):
    if isinstance(value, rdflib.URIRef):
        return f"<{value}>"
    elif isinstance(value, rdflib.Literal):
        return value.n3()
    elif isinstance(value, rdflib.BNode):
        return f"_:{value}"
    else:
        return str(value)

def upload_chunk(chunk, index):
    triples_str = "\n".join(
        f"{sparql_escape(s)} {sparql_escape(p)} {sparql_escape(o)} ." for s, p, o in chunk
    )
    query = f"""
    INSERT DATA {{
      GRAPH <{named_graph}> {{
        {triples_str}
      }}
    }}
    """
    response = requests.post(
        f"{fuseki_url}/update",
        data={"update": query},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code == 200:
        print(f"Chunk {index}: Uploaded {len(chunk)} triples.")
    else:
        print(f"Chunk {index}: Failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)

for i in range(0, total, chunk_size):
    chunk = triples[i : i + chunk_size]
    upload_chunk(chunk, i // chunk_size + 1)

print("Restore complete")
