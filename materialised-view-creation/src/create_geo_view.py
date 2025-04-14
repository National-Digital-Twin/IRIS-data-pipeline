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

import os, json, requests
from dotenv import load_dotenv

load_dotenv()

fuseki_url = os.environ.get("FUSEKI_URL")
create_view_query_file = os.environ.get("CREATE_VIEW_QUERY_FILE")
record_count_query_file = os.environ.get("RECORD_COUNT_QUERY_FILE")
batch_limit = 25000

with open(create_view_query_file, "r") as f:
    view_creation_query_template = f.read()
with open(record_count_query_file, "r") as f:
    count_query = f.read()

offset = 0
page = 1

count_result = requests.post(
        f"{fuseki_url}/query",
        headers={"Content-Type": "application/sparql-query"},
        data=count_query.encode("utf-8"),
    )
data = json.loads(count_result.text)
value = data['results']['bindings'][0]['.1']['value']
count = int(value)

while offset < count:
    query = view_creation_query_template.format(LIMIT=batch_limit, OFFSET=offset)

    print(f"Sending page {page} (OFFSET {offset})")

    response = requests.post(
        f"{fuseki_url}/update",
        headers={"Content-Type": "application/sparql-update"},
        data=query.encode("utf-8"),
    )

    if response.status_code == 204:
        print(f"Page {page} OK")
        offset += batch_limit
        page += 1
        print(f"Results processed {offset}")
        print(f"Approximately {count // batch_limit - (offset / batch_limit)} pages remaining")
    else:
        print(f"Page {page} failed: HTTP {response.status_code}")
        print(response.text)
        break
