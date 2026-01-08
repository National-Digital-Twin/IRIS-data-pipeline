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

import namespaces
from ies_tool.ies_tool import RDF_TYPE, XSD, IESTool
from namespaces import data_ns, ies_building_ns, ies_ns
from rdflib import BNode, Literal, URIRef


def build_uri(ns: str, type: str) -> str:
    """
    Builds a URI which can be used to define a subject, predicate or object.

    Args:
        ns (str): The namespace of the URI.
        type (str): The resource identified by the URI.

    Returns:
        str: The URI.
    """
    return f"{ns}{type}"


def build_ies_building_uri(type: str) -> str:
    """
    Builds a URI in the IES Building namespace.

    Args:
        type (str): The resource identified by the URI.

    Returns:
        str: The URI.
    """
    return build_uri(ies_building_ns, type)


def build_ies_uri(type: str) -> str:
    """
    Builds a URI in the IES Common namespace.

    Args:
        type (str): The resource identified by the URI.

    Returns:
        str: The URI.
    """
    return build_uri(ies_ns, type)


def get_uprn(record: dict) -> str:
    """
    Fetches the value of the URPN attribute from a building record.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The UPRN of the building.
    """
    return record["UPRN"].replace(".0", "")


def get_lodgement_date(record: dict) -> str:
    """
    Fetches the value of the lodgement date attribute from a building record.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The lodgement date of the building's EPC assessment.
    """
    return record["LodgementDate"].replace("-", "")


def create_record_uri(record: dict, type: str) -> str:
    """
    Creates a URI in the data namespace (knowledge).

    Args:
        record (dict): A record representing a building.
        type (str): The resource identified by the URI.

    Returns:
        str: The data URI for the type. e.g. data:StructureUnit_12345
    """
    return f"{data_ns}{type}_{get_uprn(record)}"


def create_stateful_record_uri(record: dict, type: str) -> str:
    """
    Creates a stateful URI in the data namespace (knowledge). The state is marked by the date.

    Args:
        record (dict): A record representing a building.
        type (str): The resource identified by the URI.

    Returns:
        str: The stateful data URI for the type. e.g. data:StructureUnitState_12345_20250331
    """
    return f"{data_ns}{type}_{get_uprn(record)}_{get_lodgement_date(record)}"


def add_ies_building_type_mappings(
    ies: IESTool, subject: str, types: list[str]
) -> None:
    """
    Creates type mappings for a given subject within the IES Building domain.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        subject (str): A URI for a particular subject.
        types (list[str]): The subject's types within IES Building e.g. ['House', 'MidTerrace']

    Returns:
        None
    """
    for type in types:
        ies.add_triple(subject, RDF_TYPE, build_ies_building_uri(type))


def add_ies_type_mappings(ies: IESTool, subject: str, types: list[str]) -> None:
    """
    Creates type mappings for a given subject within the IES Common domain.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        subject (str): A URI for a particular subject.
        types (list[str]): The subject's types within IES Common e.g. ['Created']

    Returns:
        None
    """
    for type in types:
        ies.add_triple(subject, RDF_TYPE, build_ies_uri(type))


def add_state_mappings(ies: IESTool, state_of_entity: str, entities: list[str]) -> None:
    """
    Creates stateful mappings for a given subject.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        state_of_entity (str): A URI for a particular stateful subject.
        entities (list[str]): The entities a subject is a state of.

    Returns:
        None
    """
    for entity in entities:
        ies.add_triple(state_of_entity, build_ies_uri("isStateOf"), entity)


def add_part_mappings(ies: IESTool, part_of_entity: str, entities: list[str]) -> None:
    """
    Creates part mappings for a given subject.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        part_of_entity (str): A URI for a particular subject.
        entities (list[str]): The entities a subject is a part of.

    Returns:
        None
    """
    for entity in entities:
        ies.add_triple(part_of_entity, build_ies_uri("isPartOf"), entity)


def add_attribute_mapping(
    ies: IESTool,
    record: dict,
    attribute_name: str,
    attribute_types: list[str],
    whole_entity: str,
) -> str:
    """
    Creates mappings for an attribute of an entity.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        record (dict): A record representing a building.
        attribute_name (str): The name of the attribute within the record.
        attribute_types (list[str]): The types of the attribute within IES Building.
        whole_entity (str): The entity the attribute is a part of.

    Returns:
        str: The attribute's URI.
    """
    attribute_uri = create_record_uri(record, attribute_name)
    add_ies_building_type_mappings(ies, attribute_uri, attribute_types)
    add_part_mappings(ies, attribute_uri, [whole_entity])
    return attribute_uri


def add_attribute_of_state_mapping(
    ies: IESTool,
    record: dict,
    attribute_name: str,
    attribute_types: list[str],
    entity_uris: list[str],
    entity_state_uris: list[str],
) -> str:
    """
    Creates mappings for an attribute of an entity state.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        record (dict): A record representing a building.
        attribute_name (str): The name of the attribute within the record.
        attribute_types (list[str]): The types of the attribute within IES Building.
        whole_entity (str): The entity the attribute is a part of.

    Returns:
        str: The attribute's URI.
    """
    attribute_uri = create_stateful_record_uri(record, attribute_name)
    add_ies_building_type_mappings(ies, attribute_uri, attribute_types)
    add_state_mappings(ies, attribute_uri, entity_uris)
    add_part_mappings(ies, attribute_uri, entity_state_uris)
    return attribute_uri


def add_bnode_with_type_and_value(ies: IESTool, type: str, literal_value: str) -> BNode:
    """
    Create a BNode in the graph with a type and representation value.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        type (str): A type of the BNode.
        literal_value (str): The representation value of the BNode.

    Returns:
        BNode: The BNode.
    """
    bnode = BNode()
    ies.graph.add((bnode, URIRef(RDF_TYPE), URIRef(type)))
    ies.graph.add(
        (
            bnode,
            URIRef(build_ies_uri("representationValue")),
            Literal(literal_value, datatype=XSD.integer),
        )
    )
    return bnode


def add_bnode_with_ies_type_and_value(
    ies: IESTool, type: str, literal_value: str
) -> BNode:
    """
    Create a BNode in the graph with an IES Common type and representation value.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        type (str): A type of the BNode.
        literal_value (str): The representation value of the BNode.

    Returns:
        BNode: The BNode.
    """
    return add_bnode_with_type_and_value(ies, build_ies_uri(type), literal_value)


def add_bnode_with_ies_building_type_and_value(
    ies: IESTool, type: str, literal_value: str
) -> BNode:
    """
    Create a BNode in the graph with an IES Building type and representation value.

    Args:
        ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
        type (str): A type of the BNode.
        literal_value (str): The representation value of the BNode.

    Returns:
        BNode: The BNode.
    """
    return add_bnode_with_type_and_value(
        ies, build_ies_building_uri(type), literal_value
    )


def reset_ies_graph(ies):
    ies.clear_graph()

    ies.graph.namespace_manager.bind("ies", namespaces.ies_ns)
    ies.graph.namespace_manager.bind("building", namespaces.ies_building_ns)
    ies.graph.namespace_manager.bind("data", namespaces.data_ns)
    ies.graph.namespace_manager.bind("iesuncertainty", namespaces.ies_uncertainty_ns)
    ies.graph.namespace_manager.bind("epc", namespaces.epc_ns)
    ies.graph.namespace_manager.bind("geoplace", namespaces.geoplace_ns)
    ies.graph.namespace_manager.bind("qudt", namespaces.qudt)
    ies.graph.namespace_manager.bind("unit", namespaces.qudt_unit)
    ies.graph.namespace_manager.bind("quantitykind", namespaces.qudt_quantitykind)
