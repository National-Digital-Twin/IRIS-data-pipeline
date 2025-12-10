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

from ies_tool.ies_tool import IESTool
from models.structure_unit import StructureUnit
from namespaces import iso8601_ns
from utils import (
    add_ies_building_type_mappings,
    build_ies_building_uri,
    create_record_uri,
)


class HeatingSystem:

    def __init__(self, ies: IESTool, record: dict, structure_unit_state_uri: str):
        """
        A class to represent heating system of a StructureUnit in RDF format.

        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            structure_unit (StructureUnitState): An instance of `StructureUnit`, including the state of the structure unit at
                the time of the assessment.
        """

        self.fuel_type_map: dict = {
            "Anthracite": "Anthracite",
            "Fuel": "Fuel",
            "Biomass": "Biomass",
            "Coal": "Coal",
            "Fuel": "Fuel",
            "Electricity": "Electricity",
            "LPG": "LPG",
            "NaturalFuelGas": "NaturalFuelGas",
            "Oil": "Oil",
            "SmokelessCoal": "SmokelessCoal",
            "WoodChips": "WoodChips",
            "WoodLogs": "WoodLogs",
            "WoodPellets": "WoodPellets",
            "NULL", None
        }

        self.ies = ies
        self.record = record
        self.structure_unit_state_uri = structure_unit_state_uri
        self.add_heatingsystem_mapping(record)

    def add_heatingsystem_mapping(self, record: dict) -> None:
        """
        Adds the heating system mapping.

        Args:
            record (dict): A record representing a building.

        Returns:
            None

        """

        # get fuel type from data
        fuel_type = record.get("MainFuelType")

        # get fuel type class from IES building
        fuel_type_ies_building = self.fuel_type_map[fuel_type]

        # instaniate a technical system
        self.heating_system = create_record_uri(record, type="HeatingSystem")

        # link technical system back to IES building
        add_ies_building_type_mappings(self.ies, self.heating_system, ["HeatingSystem"])

        # link technical system with structure unit
        self.ies.add_triple(
            self.structure_unit_state_uri,
            build_ies_building_uri("isServicedBy"),
            self.heating_system,
        )

        # link technical system with fuel type
        self.ies.add_triple(
            self.heating_system,
            build_ies_building_uri("isOperableWithFuel"),
            build_ies_building_uri(fuel_type_ies_building),
        )
