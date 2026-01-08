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

class Window:
    """
    A class representing the `Window`(s) within a `StructureUnit`, where insulation of the `Window` forms
    part of an Energy Performance Certificate (EPC) assessment.
    """
        
    def __init__(self, ies: IESTool, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str):
        """
        Initializes the `Window` class and adds the common mapping as well as specific insulation mappings.
        
        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        """
        self.ies = ies
        self.add_window_mapping(record)
        self.add_window_insulation_mapping(record, structure_unit_state_uri, epc_assessment_uri)
        
    def add_window_mapping(self, record: dict) -> None:
        """
        Adds the core window mapping, including the window's type and its inclusion in the `StructureUnit`.
        
        Args:
            record (dict): A record representing a building.

        Returns:
            None
        """
        self.all_asssessed_window_uri = add_attribute_mapping(self.ies, record, "AllAssessedWindows", ["AllAssessedWindows"], create_record_uri(record, "StructureUnit"))
        
    def add_window_insulation_mapping(self, record: dict, structure_unit_state_uri: str, epc_assessment_uri: str) -> None:
        """
        Adds insulation-specific mapping, including what type of glazing the windows had at the point in time
        when the EPC assessment took place.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_state_uri (str): The URI of the building's structure unit state at the tme of the EPC assessment.            
            epc_assessment_uri (str): The URI of the EPC assessment.
        
        Returns:
            None
        """
        
        window_glazing = (record.get("MultipleGlazingType") or "").strip()
        # Always create the assessment container so EPC structure is present
        assess_window_insulation_uri = add_attribute_of_state_mapping(
            self.ies,
            record,
            "AssessWindowInsulation",
            ["AssessWindowInsulation"],
            [],
            [epc_assessment_uri],
        )

        # If no glazing detail, stop here (no glazing state)
        if not window_glazing or window_glazing.upper() == "NULL":
            return

        self.window_glazing_state_uri = add_attribute_of_state_mapping(
            self.ies,
            record,
            f"AllAssessedWindows{window_glazing}",
            ["AllAssessedWindows", window_glazing],
            [self.all_asssessed_window_uri],
            [structure_unit_state_uri],
        )
        self.ies.add_triple(
            assess_window_insulation_uri,
            build_ies_building_uri("assessedStateForEnergyPerformance"),
            self.window_glazing_state_uri,
        )