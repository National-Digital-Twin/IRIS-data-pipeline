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

from utils import (add_attribute_of_state_mapping,
                   create_record_uri,
                   build_ies_uri,
                   add_ies_building_type_mappings,
                   add_part_mappings,
                   create_stateful_record_uri,
                   add_state_mappings
                   )
from ies_tool.ies_tool import IESTool
from namespaces import data_ns

class StructureUnit:
    """
    A class representing the `StructureUnit`(s) within a `Building`.
    
    Attributes:
        uri (str): The URI of the `StructureUnit`
        state_uri (str): The URI of the `StructureUnitState`
    """
    
    uri: str
    state_uri: str
    
    def __init__(self, ies: IESTool, record: dict, building_uri: str):
        """
        Initializes the `StructureUnit` class and adds the common mapping as well as a mapping for the state at the
        time of the EPC assessment and attributes about the state of the `StructureUnit`, such as the main purpose of use 
        (e.g. `ResidentialDwelling`), type of structure unit (e.g. `House`) and built form (e.g. `MidTerrace`).
        
        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            building_uri (str): The URI of the building's structure unit state at the time of the EPC assessment.
        """
        self.ies = ies
        self.uri = self.add_structure_unit_mapping(record, building_uri, 
            self.get_building_identifiers(record), self.get_locations(record))
        self.state_uri = self.add_structure_unit_state_mapping(record, self.uri)
        main_purpose_of_use = "ResidentialDwelling" if record["CertificateType"] == "domestic" else "Commercial"
        add_attribute_of_state_mapping(ies, record, "MainPurposeOfUse", [main_purpose_of_use], 
            [self.uri], [self.state_uri])
        if (record["CertificateType"] == "domestic"):
            add_attribute_of_state_mapping(ies, record, "StructureUnitType", [record.get("PropertyType")], 
                [self.uri], [self.state_uri])
            add_attribute_of_state_mapping(ies, record, "BuiltForm", [record.get("BuiltForm")], 
                [self.uri], [self.state_uri])
    
    def get_building_identifiers(self, record: dict) -> list[str]:
        """
        Creates URIs for the resources used to identify a building (i.e. the UPRN, the first line of the address, the TOID
        and the postcode).
        
        Args:
            record (dict): A record representing a building.

        Returns:
            list[str]: A list of URIs of the identifiers used for a building.
        """
        uprn_uri = create_record_uri(record, "UPRN")
        first_line_of_address_uri = create_record_uri(record, "FirstLineOfAddress")
        toid_uri = create_record_uri(record, "TOID")
        postcode_uri = f"{data_ns}PCODE_{record['Postcode'].replace(' ', '_')}"
        return [uprn_uri, first_line_of_address_uri, toid_uri, postcode_uri]
    
    def add_identifiers(self, subject: str, identifiers: list[str]) -> None:
        """
        Adds `isIdentifiedBy` triples given a subject and list of identifiers. 

        Args:
            subject (str): A resource with identifiers.
            identifiers (list[str]): A list of identifiers.

        Returns:
            None
        """
        for identifier in identifiers:
            self.ies.add_triple(subject, build_ies_uri("isIdentifiedBy"), identifier)

    def get_locations(self, record: dict) -> list[str]:
        """
        Creates URIs for the locations used to identify a building (i.e. the `Location`, the `AddressableLocation` and 
        the `LocationPoint`).

        Args:
            record (dict): A record representing a building.

        Returns:
            list[str]: A list of URIs of the locations used to identify a building.
        """
        location_uri = create_record_uri(record, "Location")
        addressable_location_uri = create_record_uri(record, "AddressableLocation")
        location_point_uri = create_record_uri(record, "LocationPoint")
        return [location_uri, addressable_location_uri, location_point_uri]

    def add_locations(self, subject: str, locations: list[str]) -> None:
        """
        Adds `inLocation` triples given a subject and list of locations.

        Args:
            subject (str): A resource in a location.
            locations (list[str]): A list of locations.

        Returns:
            None
        """
        for location in locations:
            self.ies.add_triple(subject, build_ies_uri("inLocation"), location)
    
    def add_structure_unit_mapping(self, record: dict, building_uri: str, identifiers: list[str], locations: list[str]) -> str:
        """
        Adds the core structure unit mapping.
        
        Args:
            record (dict): A record representing a building.
            building_uri (str): The URI of the building's structure unit state at the time of the EPC assessment.
            identifiers (list[str]): A list of identifiers.
            locations (list[str]): A list of locations.

        Returns:
            str: The URI of the building's structure unit.
        """
        structure_unit_uri = create_record_uri(record, "StructureUnit")
        add_ies_building_type_mappings(self.ies, structure_unit_uri, ["StructureUnit"])
        self.add_locations(structure_unit_uri, locations)
        self.add_identifiers(structure_unit_uri, identifiers)
        add_part_mappings(self.ies, structure_unit_uri, [building_uri])
        return structure_unit_uri
    
    def add_structure_unit_state_mapping(self, record: dict, structure_unit_uri: str) -> str:
        """
        Adds a mapping which captures the state of the structure unit at the time of the EPC assessment.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_uri (str): The URI of the building's structure unit.

        Returns:
            str: The URI of the building's structure unit state.
        """
        structure_unit_state_uri = create_stateful_record_uri(record, "StructureUnitState")
        add_ies_building_type_mappings(self.ies, structure_unit_state_uri, ["StructureUnitState"])
        add_state_mappings(self.ies, structure_unit_state_uri, [structure_unit_uri])
        return structure_unit_state_uri
