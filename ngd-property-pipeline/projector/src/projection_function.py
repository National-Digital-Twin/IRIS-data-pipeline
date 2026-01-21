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


import json

from sqlalchemy import text
from sqlalchemy.engine import Connection

EXISTING_EPC_RECORD_QUERY = """
    SELECT 1 FROM iris.epc_assessment e
    LEFT JOIN iris.structure_unit s ON s.epc_assessment_id = e.id
    WHERE e.uprn = :uprn;
"""

EXISTING_STRUCTURE_UNIT_RECORD_QUERY = """
    SELECT 1 FROM iris.structure_unit WHERE uprn = :uprn;
"""

EXISTING_BUILDING_RECORD_QUERY = """
    SELECT 1 FROM iris.building WHERE uprn = :uprn;
"""

UPDATE_STRUCTURE_UNIT_RECORD_QUERY = """
    UPDATE iris.structure_unit s SET
        has_roof_solar_panels = :has_roof_solar_panels,
        roof_material = :roof_material,
        roof_aspect_area_facing_north_m2 = :roof_aspect_area_facing_north_m2,
        roof_aspect_area_facing_east_m2 = :roof_aspect_area_facing_east_m2,
        roof_aspect_area_facing_south_m2 = :roof_aspect_area_facing_south_m2,
        roof_aspect_area_facing_west_m2 = :roof_aspect_area_facing_west_m2,
        roof_aspect_area_facing_north_east_m2 = :roof_aspect_area_facing_north_east_m2,
        roof_aspect_area_facing_south_east_m2 = :roof_aspect_area_facing_south_east_m2,
        roof_aspect_area_facing_south_west_m2 = :roof_aspect_area_facing_south_west_m2,
        roof_aspect_area_facing_north_west_m2 = :roof_aspect_area_facing_north_west_m2,
        roof_aspect_area_indeterminable_m2 = :roof_aspect_area_indeterminable_m2,
        roof_shape = :roof_shape
    FROM iris.epc_assessment e
    WHERE s.epc_assessment_id = e.id
    AND e.uprn = :uprn;
"""

INSERT_STRUCTURE_UNIT_RECORD_QUERY = """
    INSERT INTO iris.structure_unit(
        has_roof_solar_panels,
        roof_material,
        roof_aspect_area_facing_north_m2,
        roof_aspect_area_facing_east_m2,
        roof_aspect_area_facing_south_m2,
        roof_aspect_area_facing_west_m2,
        roof_aspect_area_facing_north_east_m2,
        roof_aspect_area_facing_south_east_m2,
        roof_aspect_area_facing_south_west_m2,
        roof_aspect_area_facing_north_west_m2,
        roof_aspect_area_indeterminable_m2,
        uprn,
        roof_shape
    )
    VALUES (
        :has_roof_solar_panels,
        :roof_material,
        :roof_aspect_area_facing_north_m2,
        :roof_aspect_area_facing_east_m2,
        :roof_aspect_area_facing_south_m2,
        :roof_aspect_area_facing_west_m2,
        :roof_aspect_area_facing_north_east_m2,
        :roof_aspect_area_facing_south_east_m2,
        :roof_aspect_area_facing_south_west_m2,
        :roof_aspect_area_facing_north_west_m2,
        :roof_aspect_area_indeterminable_m2,
        :uprn,
        :roof_shape
    );
"""


def __get_uprn_refs(record: dict):
    if "uprnreference" in record.keys():
        # data is given with single quotes e.g. "[{'uprn': 10010726548...
        uprn_reference = record["uprnreference"].replace("'", '"')
        return json.loads(uprn_reference)
    else:
        return []


def get_uprns(record: dict):
    uprn_refs = __get_uprn_refs(record)
    return [str(ref["uprn"]) for ref in uprn_refs]


def has_solar_panels(record: dict):
    solar_panels = record["roofmaterial_solarpanelpresence"]
    return solar_panels == "Present"


def get_nullable_numerical_field(record: dict, field: str):
    value = record[field]
    if value is not None and value != "":
        return value
    else:
        return 0


def project_func(connection: Connection, record: dict) -> str:
    """
    Projects a record into the database

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The RDF graph serialized into triples.
    """

    uprns = get_uprns(record)
    for uprn in uprns:
        params = {
            "uprn": uprn,
            "has_roof_solar_panels": has_solar_panels(record),
            "roof_material": record["roofmaterial_primarymaterial"],
            "roof_aspect_area_facing_north_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingnorth_m2"
            ),
            "roof_aspect_area_facing_east_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingeast_m2"
            ),
            "roof_aspect_area_facing_south_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingsouth_m2"
            ),
            "roof_aspect_area_facing_west_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingwest_m2"
            ),
            "roof_aspect_area_facing_north_east_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingnortheast_m2"
            ),
            "roof_aspect_area_facing_south_east_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingsoutheast_m2"
            ),
            "roof_aspect_area_facing_south_west_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingsouthwest_m2"
            ),
            "roof_aspect_area_facing_north_west_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areafacingnorthwest_m2"
            ),
            "roof_aspect_area_indeterminable_m2": get_nullable_numerical_field(
                record, "roofshapeaspect_areaindeterminable_m2"
            ),
            "roof_shape": record["roofshapeaspect_shape"],
        }
        query = None

        existing_epc_record = connection.execute(
            text(EXISTING_EPC_RECORD_QUERY), {"uprn": uprn}
        )
        existing_structure_unit_record = connection.execute(
            text(EXISTING_STRUCTURE_UNIT_RECORD_QUERY), {"uprn": uprn}
        )
        if (
            existing_epc_record.rowcount > 0
            or existing_structure_unit_record.rowcount > 0
        ):
            query = text(UPDATE_STRUCTURE_UNIT_RECORD_QUERY)
        else:
            existing_building_record = connection.execute(
                text(EXISTING_BUILDING_RECORD_QUERY), {"uprn": uprn}
            )
            if existing_building_record.rowcount == 1:
                query = text(INSERT_STRUCTURE_UNIT_RECORD_QUERY)

        if query is not None:
            connection.execute(query, params)
