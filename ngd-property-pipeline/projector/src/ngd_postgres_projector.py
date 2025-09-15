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

from generic_projectors.postgres_projector import GenericPostgresProjector
from ia_map_lib.config import Configurator
from dotenv import load_dotenv
import json

load_dotenv()
config = Configurator()
DB_HOST = config.get(
    "DB_HOST",
    required=True,
    description="Specifies the host for the database.",
)
DB_PORT = config.get(
    "DB_PORT",
    required=True,
    description="Specifies the port for the database.",
)
DB_NAME = config.get(
    "DB_NAME",
    required=True,
    description="Specifies the port for the database.",
)
DB_USERNAME = config.get(
    "DB_USERNAME",
    required=True,
    description="Specifies the username for the database.",
)
DB_PASSWORD = config.get(
    "DB_PASSWORD",
    required=True,
    description="Specifies the password for the database.",
)

DEBUG_MODE = True  # output to local file if True

class NgdPostgresProjector(GenericPostgresProjector):
    def get_uprn(self, record: dict):
        return record["uprn"]


    def get_uprn_refs(self, record: dict):
        if ("uprnreference" in record.keys()):
            # data is given with single quotes e.g. "[{'uprn': 10010726548...
            uprn_reference = record["uprnreference"].replace("'", "\"")
            return json.loads(uprn_reference)
        else:
            return []
            


    def get_uprns(self, record: dict):
        uprn_refs = self.get_uprn_refs(record)
        return [ref["uprn"] for ref in uprn_refs]


    def has_solar_panels(self, record: dict):
        solar_panels = record['roofmaterial_solarpanelpresence']
        return solar_panels == 'Present'
    
    
    def get_nullable_numerical_field(self, record: dict, field: str):
        value = record[field]
        if value is not None and value != "":
            return value
        else:
            return 0
    

    def project_record(self, record: dict) -> str:
        """
        Projects a record into the database
        
        Args:
            record (dict): A record representing a building.
            
        Returns:
            str: The RDF graph serialized into triples.
        """
        self.logger.debug("Beginning projection")
        
        uprns = self.get_uprns(record)
        for uprn in uprns:
            existing_epc_record = self.execute_sql(f"SELECT 1 FROM iris.epc_assessment e LEFT JOIN iris.structure_unit s ON s.epc_assessment_id = e.id \
                WHERE e.uprn = '{uprn}';")
            existing_record = self.execute_sql(f"SELECT 1 FROM iris.structure_unit WHERE uprn = '{uprn}';")
            if existing_epc_record.rowcount > 0 or existing_record.rowcount > 0:
                query = f"""
                    UPDATE iris.structure_unit s SET
                        has_roof_solar_panels = {self.has_solar_panels(record)},
                        roof_material = '{record['roofmaterial_primarymaterial']}',
                        roof_aspect_area_facing_north_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingnorth_m2')},
                        roof_aspect_area_facing_east_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingeast_m2')},
                        roof_aspect_area_facing_south_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingsouth_m2')},
                        roof_aspect_area_facing_west_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingwest_m2')},
                        roof_aspect_area_facing_north_east_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingnortheast_m2')},
                        roof_aspect_area_facing_south_east_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingsoutheast_m2')},
                        roof_aspect_area_facing_south_west_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingsouthwest_m2')},
                        roof_aspect_area_facing_north_west_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingnorthwest_m2')},
                        roof_aspect_area_indeterminable_m2 = {self.get_nullable_numerical_field(record, 'roofshapeaspect_areaindeterminable_m2')},
                        roof_shape = '{record['roofshapeaspect_shape']}'
                        FROM iris.epc_assessment e
                        WHERE s.epc_assessment_id = e.id
                        AND e.uprn = '{uprn}';
                """
            else:
                existing_building_record = self.execute_sql(f"SELECT 1 FROM iris.building WHERE uprn = '{uprn}';")
                if existing_building_record.rowcount == 0:
                    insert_building_query = f"INSERT INTO iris.building(uprn) VALUES ('{uprn}');"
                    self.execute_sql(insert_building_query)
                query = f"INSERT INTO iris.structure_unit( \
	                has_roof_solar_panels, roof_material, roof_aspect_area_facing_north_m2, roof_aspect_area_facing_east_m2, \
                    roof_aspect_area_facing_south_m2, roof_aspect_area_facing_west_m2, roof_aspect_area_facing_north_east_m2, \
                    roof_aspect_area_facing_south_east_m2, roof_aspect_area_facing_south_west_m2, roof_aspect_area_facing_north_west_m2, \
                    roof_aspect_area_indeterminable_m2, uprn, roof_shape) \
                	VALUES ({self.has_solar_panels(record)}, '{record['roofmaterial_primarymaterial']}', \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingnorth_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingeast_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingsouth_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingwest_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingnortheast_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingsoutheast_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingsouthwest_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areafacingnorthwest_m2')}, \
                            {self.get_nullable_numerical_field(record, 'roofshapeaspect_areaindeterminable_m2')}, \
                            '{uprn}', '{record['roofshapeaspect_shape']}');"

            self.execute_sql(query)
    
if __name__ == "__main__":
    projector = NgdPostgresProjector(db_url=f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    projector.run_projector()