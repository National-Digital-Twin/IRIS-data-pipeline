# SPDX-License-Identifier: Apache-2.0
# Originally developed by Telicent Ltd.; subsequently adapted, enhanced, and maintained by the National Digital Twin Programme.

#
# Copyright (C) Telicent Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#  Modifications made by the National Digital Twin Programme (NDTP)
#  © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
#  and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import ies_tool.ies_tool as ies_tool
from models.structure_unit import StructureUnit
from models.floor import Floor
from models.roof import Roof
from models.wall import Wall
from models.window import Window
from models.epc_assessment import EpcAssessment
from models.heating_system import HeatingSystem
import namespaces
from utils import create_record_uri, add_ies_building_type_mappings, build_ies_uri, get_uprn, create_stateful_record_uri
import os

DEBUG_MODE = False # output to local file if True

ies = ies_tool.IESTool(namespaces.data_ns)

def bind_namespaces() -> None:
    """
    Binds namespaces required for this graph.
    Args:
        None
        
    Returns:
        None
    """
    ies.graph.namespace_manager.bind("ies", namespaces.ies_ns)
    ies.graph.namespace_manager.bind("building", namespaces.ies_building_ns)
    ies.graph.namespace_manager.bind("data", namespaces.data_ns)
    ies.graph.namespace_manager.bind("iesuncertainty", namespaces.ies_uncertainty_ns)
    ies.graph.namespace_manager.bind("epc", namespaces.epc_ns)
    ies.graph.namespace_manager.bind("geoplace", namespaces.geoplace_ns)
    ies.graph.namespace_manager.bind("qudt", namespaces.qudt)
    ies.graph.namespace_manager.bind("unit", namespaces.qudt_unit)
    ies.graph.namespace_manager.bind("quantitykind", namespaces.qudt_quantitykind)
    

def add_building_mapping(record: dict) -> str:
    """
    Adds the common mapping for a Building entity.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        str: The building URI.
    """
    building_uri = create_record_uri(record, "Building")
    add_ies_building_type_mappings(ies, building_uri, ["Building"])
    ies.add_triple(building_uri, build_ies_uri("inLocation"), create_record_uri(record, "Location"))
    return building_uri

def main_graph_map(record: dict):
    """
    Creates triples for the main graph.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        str: The RDF graph serialized into triples.
    """
    
    uprn = get_uprn(record)
    building_uri = add_building_mapping(record)
    structure_unit = StructureUnit(ies, record, building_uri)
    
    # only add more detail if the certificate is related to a domestic property
    if record["CertificateType"] == "domestic":
        epc_assessment = EpcAssessment(ies, record, structure_unit)
        Floor(ies, record, structure_unit.state_uri, epc_assessment.uri)
        Roof(ies, record, structure_unit.state_uri, epc_assessment.uri)
        Wall(ies, record, structure_unit.state_uri, epc_assessment.uri)
        Window(ies, record, structure_unit.state_uri, epc_assessment.uri)
        
    if DEBUG_MODE:
        ies.graph.serialize(destination=f"{uprn}_epc.ttl", format="turtle")
        return

    return ies.graph.serialize(format="nt")

def heating_graph_map(record: dict):
    """
    Creates triples for the heating system graph.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        str: The RDF graph serialized into triples."""
    
    uprn = get_uprn(record)

    structure_unit_state_uri = create_stateful_record_uri(record, "StructureUnitState")

    # only add more detail if the certificate is related to a domestic property
    if record["CertificateType"] == "domestic":
        HeatingSystem(ies, record, structure_unit_state_uri)

    if DEBUG_MODE:
        ies.graph.serialize(destination=f"{uprn}_epc.ttl", format="turtle")
        return

    return ies.graph.serialize(format="nt")

def map_func(record: dict) -> str:
    """
    Creates the graph of choice and orchestrates its mappings.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        str: The RDF graph serialized into triples.
    """

    ies.clear_graph()
    bind_namespaces()

    map_function = os.getenv("MAP_FUNC")

    if map_function == "MAIN":
        return main_graph_map(record)
    elif map_function == "HEATING":
        return heating_graph_map(record)
    else:
        return main_graph_map(record)

