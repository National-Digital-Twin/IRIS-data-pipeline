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
import uuid

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

class AddressProfilingProjector(GenericPostgresProjector):

    fuel_type_map: dict = {
        "Anthracite": "Anthracite",
        "Biogas": "Fuel",
        "Biomass": "Biomass",
        "Coal": "Coal",
        "DualFuel": "Fuel",
        "Electricity": "Electricity",
        "LPG": "LPG",
        "MainsGas": "NaturalFuelGas",
        "Oil": "Oil",
        "Other": "Fuel",
        "SmokelessCoal": "SmokelessCoal",
        "WoodChips": "WoodChips",
        "WoodLogs": "WoodLogs",
        "WoodPellets": "WoodPellets"
    }
    
    wall_construction_map = {
        "CavityWall": "CavityWall",
        "Cob": "Cob",
        "GraniteOrWhinstone": "GraniteOrWhinstone",
        "ParkHomeWall": "ParkHomeWall",
        "Sandstone": "Sandstone",
        "SolidBrick": "SolidBrick",
        "SystemBuilt": "SystemBuilt",
        "TimberFrame": "TimberFrame",
        "NULL": None,
        "": None,
        "Other": "Wall",
    }
    
    wall_insulation_map = {
        "AsBuilt": "InsulatedWall",
        "FilledCavity": "InsulatedWall",
        "FilledCavityAndInternalInsulation": "InternalInsulation",
        "FilledCavityAndExternalInsulation": "ExternalInsulation",
        "WithAdditionalInsulation": "InsulatedWall",
        "WithInternalInsulation": "InternalInsulation",
        "WithExternalInsulation": "ExternalInsulation",
        "Unknown": "WallInsulation",
        "NULL": "NoInsulationInWall",
        "": "NoInsulationInWall",
    }
    
    roof_construction_map = {
        "Flat": "FlatRoof",
        "AnotherDwellingAbove": "AnotherDwellingAbove",
        "OtherPremisesAbove": "OtherPremisesAbove",
        "Pitched": "PitchedRoof",
        "PitchedNormalLoftAccess": "PitchedRoof",
        "PitchedNormalNoLoftAccess": "PitchedRoof",
        "PitchedThatched": "ThatchedRoof",
        "PitchedWithSlopingCeiling": "PitchedRoof",
        "ParkHomeRoof": "RoofConstruction",
        "Thatched": "ThatchedRoof",
        "RoofRooms": "RoofRooms",
        "Other": "RoofConstruction",
        "NULL": None,
        "": None,
    }
    
    roof_insulation_map = {
        "Rafters": "InsulatedAtRafters",
        "InsulatedAtRafters": "InsulatedAtRafters",
        "CeilingInsulated": "CeilingInsulated",
        "Unknown": "NoInsulationInRoof",
        "None": "NoInsulationInRoof",
        "FlatRoofInsulation": "FlatRoofInsulation",
        "NoInsulation": "NoInsulationInRoof",
        "NoInsulation(Assumed)": "NoInsulationAssumedInRoof ",
        "NoInsulationAssumed": "NoInsulationAssumedInRoof",
        "LoftInsulation(Assumed)": "AssumedLoftInsulation",
        "LoftInsulation": "LoftInsulation",
        "LimitedInsulationAssumed": "LimitedInsulationAssumed",
        "LimitedInsulation": "LimitedInsulation",
        "InsulatedAssumed": "InsulatedAssumed",
        "Other": "Insulated",
        "Insulated": "Insulated",
        "Thatched": "InsulatedWithThatched",
        "ThatchedWithAdditionalInsulation": "ThatchedWithAdditionalInsulation",
        "NULL": "NoInsulationInRoof",
        "": "NoInsulationInRoof",
    }
    
    floor_construction_map: dict = {
        "Unknown": None,
        "Other": "Floor",
        "Solid": "SolidFloor",
        "SuspendedTimber": "Suspended",
        "SuspendedNotTimber": "Suspended",
        "Suspended": "Suspended",
        "OtherPremisesBelow": "OtherPremisesBelowFloor",
        "AnotherDwellingBelow": "AnotherDwellingBelowFloor",
        "NULL": None,
        "": None,
    }
    
    floor_insulation_map: dict = {
        "AsBuilt": None,
        "RetroFitted": "InsulatedFloor",
        "NoInsulation": "NoInsulationInFloor",
        "Insulated": "InsulatedFloor",
        "LimitedInsulation": "LimitedFloorInsulation",
        "NULL": None,
        "": None,
    }
    
    def get_uprn(self, record: dict):
        return record["UPRN"]   
    
    def get_sap_band(self, record: dict):
        return self.get_nullable_text_field(record["SAPBand"])
    
    def get_lodgement_date(self, record: dict):
        return self.get_nullable_text_field(record["LodgementDate"])
    
    def get_su_type(self, record: dict):
        return self.get_nullable_text_field(record["PropertyType"])
    
    def get_built_form(self, record: dict):
        return self.get_nullable_text_field(record["BuiltForm"])
    
    def get_fuel_type(self, record: dict):
        return self.get_nullable_text_field(self.fuel_type_map[record["MainFuelType"]])
    
    def get_window_glazing(self, record: dict):
        # catch anything which isn't in the mapping
        return self.get_nullable_text_field(record["MultipleGlazingType"])

    
    def get_wall_construction(self, record: dict):
        # catch anything which isn't in the mapping
        if record["WallConstruction"] in self.wall_construction_map.keys():
            return self.get_nullable_text_field(self.wall_construction_map[record["WallConstruction"]])
        else:
            return 'NULL'
    
    def get_wall_insulation(self, record: dict):
        # catch anything which isn't in the mapping
        if record["WallInsulationType"] in self.wall_insulation_map.keys():
            return self.get_nullable_text_field(self.wall_insulation_map[record["WallInsulationType"]])
        else:
            return 'NULL'

    def get_roof_construction(self, record: dict):
        
        # catch anything which isn't in the mapping
        if record["RoofConstruction"] in self.roof_construction_map.keys():
            return self.get_nullable_text_field(self.roof_construction_map[record["RoofConstruction"]])
        else:
            return 'NULL'
    
    def get_roof_insulation(self, record: dict):
        
        # catch anything which isn't in the mapping
        if record["RoofInsulationLocation"] in self.roof_insulation_map.keys():
            return self.get_nullable_text_field(self.roof_insulation_map[record["RoofInsulationLocation"]])
        else:
            return 'NULL'
    
    def get_roof_insulation_thickness(self, record: dict):
        # catch anything which isn't in the mapping
        return self.get_nullable_text_field(record["RoofInsulationThickness"])
    
    def get_floor_construction(self, record: dict):
        
        # catch anything which isn't in the mapping
        if record["FloorConstruction"] in self.floor_construction_map.keys():
            return self.get_nullable_text_field(self.floor_construction_map[record["FloorConstruction"]])
        else:
            return 'NULL'

    def get_floor_insulation(self, record: dict):
        
        # catch anything which isn't in the mapping
        if record["FloorInsulation"] in self.floor_insulation_map.keys():
            return self.get_nullable_text_field(self.floor_insulation_map[record["FloorInsulation"]])
        else:
            return 'NULL'
            
    def get_nullable_text_field(self, value: str):
        if value is not None and value != "":
            return value
        else:
            return 'NULL'
    
    def project_record(self, record: dict) -> str:
        """
        Projects a record into the database
        
        Args:
            record (dict): A record representing a building.
            
        Returns:
            str: The RDF graph serialized into triples.
        """
        self.logger.debug("Beginning projection")
        
        # get uprn
        uprn = self.get_uprn(record)
            
        # create new epc assessment id
        assessment_id = uuid.uuid4()
                    
        # insert EPC record
        query = f"""
        INSERT INTO public.epc_assessment
            (id, uprn, epc_rating, lodgement_date)
            VALUES 
            (
                '{assessment_id}', 
                {uprn}, 
                '{self.get_sap_band(record)}', 
                '{self.get_lodgement_date(record)}'
            )
        """
        self.logger.debug(query)
        self.execute_sql(query)
        
        # insert record into structure unit table
        query = f"""
        INSERT INTO public.structure_unit
            (
                epc_assessment_id, 
                type, 
                built_form, 
                fuel_type,
                window_glazing,
                wall_construction,
                wall_insulation,
                roof_construction,
                roof_insulation,
                roof_insulation_thickness,
                floor_construction,
                floor_insulation,
                uprn
                )
            VALUES 
            (
                '{assessment_id}', 
                '{self.get_su_type(record)}',
                '{self.get_built_form(record)}',
                '{self.get_fuel_type(record)}',
                '{self.get_window_glazing(record)}',
                '{self.get_wall_construction(record)}',
                '{self.get_wall_insulation(record)}',
                '{self.get_roof_construction(record)}',
                '{self.get_roof_insulation(record)}',
                '{self.get_roof_insulation_thickness(record)}',
                '{self.get_floor_construction(record)}',
                '{self.get_floor_insulation(record)}', 
                {uprn}
            )
        """
        self.logger.debug(query)
        self.execute_sql(query)
    
if __name__ == "__main__":
    projector = AddressProfilingProjector(db_url=f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    projector.run_projector()