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

from ies_tool.ies_tool import RDF_TYPE, XSD
from namespaces import data_ns, ies_ns, ies_building_ns
from rdflib import BNode, URIRef, Literal

def build_uri(ns, type):
    """
    Builds a URI which can be used to define a subject, predicate or object.
    
    Args:
        ns (str): The namespace of the URI.
        type (str): The resource identified by the URI.
    """
    return f"{ns}{type}"

def build_ies_building_uri(type):
    """
    Builds a URI in the IES Building namespace.
    
    Args:
        type (str): The resource identified by the URI.
    """
    return build_uri(ies_building_ns, type)

def build_ies_uri(type):
    """
    Builds a URI in the IES Common namespace.
    
    Args:
        type (str): The resource identified by the URI.
    """
    return build_uri(ies_ns, type)

def get_uprn(record):
    """
    Fetches the value of the URPN attribute from a building record.
    
    Args:
        record (Dict): A record representing a building.
    """
    return record["UPRN"].replace(".0", "")

def get_lodgement_date(record):
    """
    Fetches the value of the lodgement date attribute from a building record.
    
    Args:
        record (Dict): A record representing a building.
    """
    return record["LodgementDate"].replace("-", "")

def create_record_uri(record, type):
    """
    Creates a URI in the data namespace (knowledge).
    
    Args:
        record (Dict): A record representing a building.
        type (str): The resource identified by the URI.
    """
    return f"{data_ns}{type}_{get_uprn(record)}"

def create_stateful_record_uri(record, type):
    """
    Creates a stateful URI in the data namespace (knowledge). The state is marked by the date.
    
    Args:
        record (Dict): A record representing a building.
        type (str): The resource identified by the URI.
    """
    return f"{data_ns}{type}_{get_uprn(record)}_{get_lodgement_date(record)}"

def add_ies_building_type_mappings(ies, subject, types):
    for type in types:
        ies.add_to_graph(subject, RDF_TYPE, build_ies_building_uri(type))

def add_ies_type_mappings(ies, subject, types):
    for type in types:
        ies.add_to_graph(subject, RDF_TYPE, build_ies_uri(type))

def add_state_mappings(ies, state_of_entity, entities):
    for entity in entities:
        ies.add_to_graph(state_of_entity, build_ies_uri("isStateOf"), entity)

def add_part_mappings(ies, part_of_entity, entities):
    for entity in entities:
        ies.add_to_graph(part_of_entity, build_ies_uri("isPartOf"), entity)
    
def add_attribute_mapping(ies, record, attribute_name, attribute_types, whole_entity):
    attribute_uri = create_record_uri(record, attribute_name)
    add_ies_building_type_mappings(ies, attribute_uri, attribute_types)
    add_part_mappings(ies, attribute_uri, [whole_entity])
    return attribute_uri
    
def add_attribute_of_state_mapping(ies, record, attribute_name, attribute_types, entity_uris, entity_state_uris):
    attribute_uri = create_stateful_record_uri(record, attribute_name)
    add_ies_building_type_mappings(ies, attribute_uri, attribute_types)  
    add_state_mappings(ies, attribute_uri, entity_uris)  
    add_part_mappings(ies, attribute_uri, entity_state_uris)
    return attribute_uri

def add_bnode_with_type_and_value(ies, type, literal_value):
    bnode = BNode()
    ies.graph.add((bnode, URIRef(RDF_TYPE), URIRef(type)))
    ies.graph.add((bnode, URIRef(build_ies_uri("representationValue")), Literal(literal_value, datatype=XSD.integer)))
    return bnode

def add_bnode_with_ies_type_and_value(ies, type, literal_value):
    return add_bnode_with_type_and_value(ies, build_ies_uri(type), literal_value)

def add_bnode_with_ies_building_type_and_value(ies, type, literal_value):
    return add_bnode_with_type_and_value(ies, build_ies_building_uri(type), literal_value)