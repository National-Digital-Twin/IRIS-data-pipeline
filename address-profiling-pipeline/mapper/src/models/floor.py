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
                   build_ies_building_uri)
from ies_tool.ies_tool import IESTool

class Floor:
    """
    A class representing the `Floor`(s) within a `StructureUnit`, where insulation and construction of the `Floor` forms
    part of an Energy Performance Certificate (EPC) assessment.
    
    Attributes:
        floor_construction_map (dict): A map of floor constructions against IES Building ontology.
        floor_insulation_map (dict): A map of floor insulations against IES Building ontology.
    """

    floor_construction_map: dict = {
        "Solid": "Solid",
        "Suspended": "Suspended",
        "AnotherDwellingBelow": "AnotherDwellingBelow",
        "NULL": None,
    }

    floor_insulation_map: dict = {
        "InsulatedFloor": "InsulatedFloor",
        "LimitedFloorInsulation": "LimitedFloorInsulation",
        "NoInsulationInFloor": "NoInsulationInFloor",
        "NULL": None,
    }
    
    def __init__(self, ies: IESTool, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str):
        """
        Initializes the `Floor` class and adds the common mapping as well as specific insulation mappings.
        
        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        """
        self.ies = ies
        self.add_floor_mapping(record)
        self.add_floor_insulation_mapping(record, structure_unit_state_uri)
        self.add_floor_construction_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        
    def add_floor_mapping(self, record: dict) -> None:
        """
        Adds the core floor mapping.
        
        Args:
            record (dict): A record representing a building.
            
        Returns:
            None

        """
        self.all_asssessed_floors_uri = add_attribute_mapping(self.ies, record, "AllAssessedFloors", ["AllAssessedFloor"], create_record_uri(record, "Building"))
        self.all_asssessed_floor_sections_uri = add_attribute_mapping(self.ies, record, "AllAssessedFloorSections", ["AllAssessedFloorSection"], self.all_asssessed_floors_uri)
        
    def add_floor_insulation_mapping(self, record: dict, structure_unit_state_uri: str) -> None:
        """
        Adds insulation-specific mapping, including whether the floor was insulated at the point in time
        when the EPC assessment took place.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        
        Returns:
            None
        """
        floor_insulation = self.floor_insulation_map.get(record.get("FloorInsulation"))
        all_assessed_floors_insulated_uri = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedFloors{floor_insulation}", ["AllAssessedFloor", f"{floor_insulation}"], 
            [self.all_asssessed_floors_uri], [structure_unit_state_uri])
        add_attribute_of_state_mapping(self.ies, record, f"AllAssessedFloorSections{floor_insulation}", ["AllAssessedFloorSection"], 
            [], [all_assessed_floors_insulated_uri, self.all_asssessed_floor_sections_uri])
        
    def add_floor_construction_mapping(self, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str) -> None:
        """
        Adds construction-specific mapping, including the state of the floor construction at the point in time
        when the EPC assessment took place.
        
        Args:
            record (Dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        
        Returns:
            None
        """
        floor_construction = self.floor_construction_map.get(record.get("FloorConstruction"))
        all_assessed_floors_constructed_uri = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedFloors{floor_construction}", ["AllAssessedFloor", floor_construction], 
            [self.all_asssessed_floors_uri], [structure_unit_state_uri])
        all_assessed_floor_sections_constructed_uri = add_attribute_of_state_mapping(self.ies, record, f"AllAssessedFloorSections{floor_construction}", ["AllAssessedFloorSection"], 
            [], [all_assessed_floors_constructed_uri, self.all_asssessed_floor_sections_uri])
        assess_floor_construction_uri = add_attribute_of_state_mapping(self.ies, record, "AssessFloorConstruction", ["AssessFloorConstruction"], 
            [], [epc_assessment_uri])
        self.ies.add_triple(assess_floor_construction_uri, build_ies_building_uri("assessedStateForEnergyPerformance"), all_assessed_floor_sections_constructed_uri)
