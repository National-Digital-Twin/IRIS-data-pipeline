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

class Roof:
    """
    A class representing the `Roof`(s) within a `StructureUnit`, where insulation and construction of the `Roof` forms
    part of an Energy Performance Certificate (EPC) assessment.
    
    Attributes:
        roof_type_map (dict): A map of roof types against IES Building ontology.
        roof_insulation_map (dict): A map of roof insulations against IES Building ontology.
    """

    roof_type_map = {
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
    
    def __init__(self, ies: IESTool, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str):
        """
        Initializes the `Roof` class and adds the common mapping as well as specific insulation mappings.
        
        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        """
        self.ies = ies
        self.add_roof_mapping(record)
        self.add_roof_insulation_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        
    def add_roof_mapping(self, record: dict) -> None:
        """
        Adds the core roof mapping.
        
        Args:
            record (Dict): A record representing a building.
        
        Returns:
            None
        """
        self.all_asssessed_roof_uri = add_attribute_mapping(self.ies, record, "AllAssessedRoof", ["AllAssessedRoof"], create_record_uri(record, "Building"))
        self.all_assessed_roof_sections_uri = add_attribute_mapping(self.ies, record, "AllAssessedRoofSections", ["AllAssessedRoofSection"], self.all_asssessed_roof_uri)
        
    def add_roof_insulation_mapping(self, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str) -> None:
        """
        Adds insulation-specific mapping, including the location and depth of the roof insulation at the point in time
        when the EPC assessment took place.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        
        Returns:
            None
        """
        roof_types = self.get_roof_types(record)
        all_assessed_roof_state_uri = add_attribute_of_state_mapping(self.ies, record, "AllAssessedRoof", roof_types, 
            [self.all_asssessed_roof_uri], [structure_unit_state_uri])
        all_assessed_roof_sections_state_uri = add_attribute_of_state_mapping(self.ies, record, "AllAssessedRoofSections", ["AllAssessedRoofSection"], 
            [], [all_assessed_roof_state_uri, self.all_assessed_roof_sections_uri])
        assess_roof_insulation_uri = add_attribute_of_state_mapping(self.ies, record, "AssessRoofInsulation", ["DetermineRoofInsulationLocation"], 
            [], [epc_assessment_uri])
        self.ies.add_triple(assess_roof_insulation_uri, build_ies_building_uri("assessedStateForEnergyPerformance"), all_assessed_roof_sections_state_uri)
        
    def get_roof_types(self, record: dict) -> list[str]:
        """
        Gets a list of types for the roof.
        
        Args:
            record (dict): A record representing a building.

        Returns:
            list[str]: A list of types for the roof.
        """
        insulation_thickness = record.get("RoofInsulationThickness")
        roof_type = self.roof_type_map.get(record.get("RoofConstruction"))
        insulation_type = self.roof_insulation_map.get(record.get("RoofInsulationLocation"))
        roof_types = ["AllAssessedRoof", f"{insulation_type}", f"{roof_type}"]
        if (insulation_thickness):
            roof_types.append(f"{insulation_thickness}_Insulation")
        return roof_types