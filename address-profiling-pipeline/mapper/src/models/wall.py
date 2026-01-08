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

from utils import (add_attribute_mapping,
                   create_record_uri,
                   add_attribute_of_state_mapping,
                   build_ies_building_uri
                   )
from ies_tool.ies_tool import IESTool

class Wall:
    """
    A class representing the `Wall`(s) within a `StructureUnit`, where insulation and construction of the `Wall` forms
    part of an Energy Performance Certificate (EPC) assessment.
    
    Attributes:
        wall_type_map (dict): A map of wall types against IES Building ontology.
        wall_insulation_map (dict): A map of wall insulations against IES Building ontology.
    """
    
    wall_construction_type_map = {
        "CavityWall": "CavityWall",
        "Cob": "Cob",
        "GraniteOrWhinstone": "GraniteOrWhinstone",
        "ParkHomeWall": "ParkHomeWall",
        "Sandstone": "Sandstone",
        "SolidBrick": "SolidBrick",
        "SystemBuilt": "SystemBuilt",
        "TimberFrame": "TimberFrame",
        "Other": "Wall",
        "NULL": None
    }
    
    wall_insulation_type_map = {
        "InternalInsulation": "InternalInsulation",
        "ExternalInsulation": "ExternalInsulation",
        "InsulatedWall": "InsulatedWall",
        "PartialInsulation": "PartialInsulation",
        "NoInsulationInWall": "NoInsulationInWall",
        "WallInsulation": "WallInsulation",
        "NULL": None
    }
        
    def __init__(self, ies: IESTool, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str):
        """
        Initializes the `Wall` class and adds the common mapping as well as specific insulation and construction mappings.
        
        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        """
        self.ies = ies
        self.add_wall_mapping(record)
        self.add_wall_insulation_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        self.add_wall_construction_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        
    def add_wall_mapping(self, record: dict) -> None:
        """
        Adds the core wall mapping.
        
        Args:
            record (dict): A record representing a building.
        
        Returns:
            None
        """
        self.all_asssessed_wall_uri = add_attribute_mapping(self.ies, record, "AllAssessedWalls", ["AllAssessedWall"], create_record_uri(record, "Building"))
        self.all_assessed_wall_sections_uri = add_attribute_mapping(self.ies, record, "AllAssessedWallSections", ["AllAssessedWallSection"], self.all_asssessed_wall_uri)
        
    def add_wall_insulation_mapping(self, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str) -> None:
        """
        Adds insulation-specific mapping, including the location and depth of the wall  insulation at the point in time
        when the EPC assessment took place.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        
        Returns:
            None
        """
        wall_insulation = (self.wall_insulation_type_map.get(record.get("WallInsulationType")) or "").strip()
        attribute_types = ["AllAssessedWall"]
        if wall_insulation:
            attribute_types.append(wall_insulation)

        all_walls_insulation_state = add_attribute_of_state_mapping(
            self.ies,
            record,
            f"AllAssessedWalls{wall_insulation}" if wall_insulation else "AllAssessedWalls",
            attribute_types,
            [self.all_asssessed_wall_uri],
            [structure_unit_state_uri],
        )
        all_walls_sections_insulation_state = add_attribute_of_state_mapping(
            self.ies,
            record,
            f"AllAssessedWallSections{wall_insulation}" if wall_insulation else "AllAssessedWallSections",
            ["AllAssessedWallSection"],
            [],
            [all_walls_insulation_state, self.all_assessed_wall_sections_uri],
        )
        assess_wall_insulation_uri = add_attribute_of_state_mapping(
            self.ies,
            record,
            "AssessWallInsulation",
            ["AssessWallInsulation"],
            [],
            [epc_assessment_uri],
        )
        self.ies.add_triple(
            assess_wall_insulation_uri,
            build_ies_building_uri("assessedStateForEnergyPerformance"),
            all_walls_sections_insulation_state,
        )

    def add_wall_construction_mapping(self, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str) -> None:
        """
        Adds insulation-specific mapping, including the location and depth of the wall  insulation at the point in time
        when the EPC assessment took place.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        
        Returns:
            None
        """
        wall_construction = (self.wall_construction_type_map.get(record.get("WallConstruction")) or "").strip()
        attribute_types = ["AllAssessedWall"]
        if wall_construction:
            attribute_types.append(wall_construction)

        all_walls_construction_state = add_attribute_of_state_mapping(
            self.ies,
            record,
            f"AllAssessedWalls{wall_construction}" if wall_construction else "AllAssessedWalls",
            attribute_types,
            [self.all_asssessed_wall_uri],
            [structure_unit_state_uri],
        )
        all_walls_sections_construction_state = add_attribute_of_state_mapping(
            self.ies,
            record,
            f"AllAssessedWallSections{wall_construction}" if wall_construction else "AllAssessedWallSections",
            ["AllAssessedWallSection"],
            [],
            [all_walls_construction_state, self.all_assessed_wall_sections_uri],
        )
        assess_wall_construction_uri = add_attribute_of_state_mapping(
            self.ies,
            record,
            "AssessWallConstruction",
            ["AssessWallConstruction"],
            [],
            [epc_assessment_uri],
        )
        self.ies.add_triple(
            assess_wall_construction_uri,
            build_ies_building_uri("assessedStateForEnergyPerformance"),
            all_walls_sections_construction_state,
        )
