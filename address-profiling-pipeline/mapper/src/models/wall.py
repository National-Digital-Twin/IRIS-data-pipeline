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

from utils import *

class Wall:
    
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
    
    wall_type_map = {
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
        
    def __init__(self, ies, record, structure_unit_state_uri, epc_assessment_uri):
        self.ies = ies
        self.add_wall_mapping(record)
        self.add_wall_insulation_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        self.add_wall_construction_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        
    def add_wall_mapping(self, record):
        self.all_asssessed_wall_uri = add_attribute_mapping(self.ies, record, "AllAssessedWalls", ["AllAssessedWall"], create_record_uri(record, "Building"))
        self.all_assessed_wall_sections_uri = add_attribute_mapping(self.ies, record, "AllAssessedWallSections", ["AllAssessedWallSection"], self.all_asssessed_wall_uri)
        
    def add_wall_insulation_mapping(self, record, structure_unit_state_uri, epc_assessment_uri):
        wall_insulation = self.wall_insulation_map.get(record.get("WallInsulationType"))
        all_walls_insulation_state = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedWalls{wall_insulation}", ["AllAssessedWall", f"{wall_insulation}"], 
            [self.all_asssessed_wall_uri], [structure_unit_state_uri])
        all_walls_sections_insulation_state = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedWallSections{wall_insulation}", ["AllAssessedWallSection"], 
            [], [all_walls_insulation_state, self.all_assessed_wall_sections_uri])
        assess_wall_insulation_uri = add_attribute_of_state_mapping(self.ies, record, f"AssessWallInsulation", ["AssessWallInsulation"], 
            [], [epc_assessment_uri])
        self.ies.add_triple(assess_wall_insulation_uri, build_ies_building_uri("assessedStateForEnergyPerformance"), all_walls_sections_insulation_state)

    def add_wall_construction_mapping(self, record, structure_unit_state_uri, epc_assessment_uri):
        wall_construction = record.get("WallConstruction")
        all_walls_construction_state = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedWalls{wall_construction}", ["AllAssessedWall", f"{wall_construction}"], 
            [self.all_asssessed_wall_uri], [structure_unit_state_uri])
        all_walls_sections_construction_state = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedWallSections{wall_construction}", ["AllAssessedWallSection"], 
            [], [all_walls_construction_state, self.all_assessed_wall_sections_uri])
        assess_wall_construction_uri = add_attribute_of_state_mapping(self.ies, record, f"AssessWallConstruction", ["AssessWallConstruction"], 
            [], [epc_assessment_uri])
        self.ies.add_triple(assess_wall_construction_uri, build_ies_building_uri("assessedStateForEnergyPerformance"), all_walls_sections_construction_state)