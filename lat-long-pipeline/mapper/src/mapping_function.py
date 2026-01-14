# SPDX-License-Identifier: Apache-2.0

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

# This file is unmodified from its original version developed by Telicent Ltd.,
# and is now included as part of a repository maintained by the National Digital Twin Programme.
# All support, maintenance and further development of this code is now the responsibility
# of the National Digital Twin Programme.

import ies_tool.ies_tool as ies_tool
from ies_tool.ies_tool import RDF_TYPE, XSD
import hashlib
from typing import Optional
from rdflib import BNode, Literal, Namespace, URIRef

DEBUG_MODE = False  # output to local file if True

# declare namespaces
ies_ns = "http://informationexchangestandard.org/ont/ies#"
ies_building_ns = "http://ies.data.gov.uk/ontology/ies-building1#"
rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
data_ns = "http://ndtp.co.uk/data#"
geoplace_ns = "https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn#"

GEO = Namespace("http://www.opengis.net/ont/geosparql#")

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

ies = ies_tool.IESTool(data_ns)

def get_uprn(record: dict):
    """
    Fetches the value of the URPN attribute from a building record.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        str: The UPRN of the building.
    """
    return record["UPRN"].replace(".0", "")
    
def add_typed_field(record: dict, type: str, type_ns: str, record_field: str) -> str:
    """
    Creates type mapping for a given record field within a given namespace.
    
    Args:
        record (dict): A record representing a building.
        type (str): The name of the type within the namespace. e.g. TOID
        type_ns (str): The namespace containing the type. e.g. ies
        record_field (str): The name of the record key e.g. TOID
        
    Returns:
        str: The URI of the created field with type.
    """
    value = record[record_field]
    identifier_uri = create_record_uri(record, type)
    ies.add_triple(identifier_uri, RDF_TYPE, build_uri(type_ns, type))
    ies.add_triple(subject=identifier_uri, predicate=build_ies_uri("representationValue"), obj=value, 
                   is_literal=True, literal_type="string")
    return identifier_uri
    
def add_typed_identifier(record: dict, subject: str, type: str, type_ns: str, record_field: str) -> None:
    """
    Creates type mapping for an identifying field within a given namespace and adds it as an identifier of subject.
    
    Args:
        record (dict): A record representing a building.
        subject (str): The subject being identified.
        type (str): The name of the type within the namespace. e.g. TOID
        type_ns (str): The namespace containing the type. e.g. ies
        record_field (str): The name of the record key e.g. TOID
        
    Returns:
        None
    """
    identifier_uri = add_typed_field(record, type, type_ns, record_field)
    ies.add_triple(subject, predicate=build_ies_uri("isIdentifiedBy"), obj=identifier_uri)
    
def add_postcode_identifier(record: dict, addressable_location: str) -> None:
    """
    Creates mapping for postcode.
    
    Args:
        record (dict): A record representing a building.
        addressable_location (str): The URI of an addressable location.
        
    Returns:
        None
    """
    postcode = record.get("Postcode")
    identifier_uri = f"{data_ns}PCODE_{postcode.replace(' ', '_')}"
    ies.add_triple(identifier_uri, RDF_TYPE, build_ies_uri("PostalCode"))
    ies.add_triple(subject=identifier_uri, predicate=build_ies_uri("representationValue"), obj=postcode, 
                   is_literal=True, literal_type="string")
    ies.add_triple(addressable_location, predicate=ies_ns + "isIdentifiedBy", obj=identifier_uri)
    

def add_addressable_location_identifiers(record: dict, addressable_location: str) -> None:
    """
    Creates identifiers for an addressable location.
    
    Args:
        record (dict): A record representing a building.
        addressable_location (str): The URI of an addressable location.
        
    Returns:
        None
    """
    add_typed_identifier(record, addressable_location, "UPRN", ies_building_ns, "UPRN")
    add_typed_identifier(record, addressable_location, "FirstLineOfAddress", ies_ns, "Address")
    add_typed_field(record, "TOID", ies_ns, "TOID")
    add_postcode_identifier(record, addressable_location)
    

def add_bnode_with_ies_type_and_value(type: str, literal_value: str) -> BNode:
    """
    Create a BNode in the graph with a type and representation value.
    
    Args:
        type (str): A type of the BNode.
        literal_value (str): The representation value of the BNode.
        
    Returns:
        BNode: The BNode.
    """
    bnode = BNode()
    ies.graph.add((bnode, URIRef(RDF_TYPE), URIRef(build_ies_uri(type))))
    ies.graph.add((bnode, URIRef(build_ies_uri("representationValue")), Literal(literal_value, datatype=XSD.string)))
    return bnode

def add_geographic_mapping(record: dict) -> None:
    """
    Creates the core geographic mappings.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        None
    """
    location_point_uri = create_record_uri(record, "LocationPoint")
    ies.add_triple(subject=location_point_uri, predicate=RDF_TYPE, obj=build_ies_uri("PointOnEarthSurface"))
    
    long = record.get("Longitude")
    long_node = add_bnode_with_ies_type_and_value("Longitude", long)
    ies.graph.add((URIRef(location_point_uri), URIRef(build_ies_uri("isIdentifiedBy")), long_node))
    lat = record.get("Latitude")
    lat_node = add_bnode_with_ies_type_and_value("Latitude", lat)
    ies.graph.add((URIRef(location_point_uri), URIRef(build_ies_uri("isIdentifiedBy")), lat_node))
    
    wkt_literal = Literal(f"POINT({long} {lat})", datatype=GEO.wktLiteral)
    wkt_bnode = BNode()
    ies.graph.add((wkt_bnode, URIRef(RDF_TYPE), URIRef(build_ies_uri("ISO19125-WKT"))))
    ies.graph.add((wkt_bnode, URIRef(build_ies_uri("representationValue")), wkt_literal))
    ies.graph.add((wkt_bnode, GEO.asWKT, wkt_literal))
    ies.graph.add((URIRef(location_point_uri), URIRef(build_ies_uri("isRepresentedAs")), wkt_bnode))
    ies.graph.add((URIRef(location_point_uri), GEO.hasGeometry, wkt_bnode))


def map_func(record: dict) -> Optional[str]:
    """
    Creates the graph and orchestrates its mappings.
    
    Args:
        record (dict): A record representing a building.
        
    Returns:
        str: The RDF graph serialized into triples
    """
    ies.clear_graph()
    # first our namespaces
    ies.graph.namespace_manager.bind("building", ies_building_ns)
    ies.graph.namespace_manager.bind("data", data_ns)
    ies.graph.namespace_manager.bind("geoplace", geoplace_ns)
    ies.graph.namespace_manager.bind("ies", ies_ns)

    addressable_location_uri = create_record_uri(record, "AddressableLocation")
    ies.add_triple(addressable_location_uri, RDF_TYPE, build_ies_building_uri("AddressableLocation"))
    add_addressable_location_identifiers(record, addressable_location_uri)
    
    location_uri = create_record_uri(record, "Location")
    ies.add_triple(location_uri, RDF_TYPE, build_ies_uri("Location"))
    add_postcode_identifier(record, location_uri)
    
    add_geographic_mapping(record)

    if DEBUG_MODE:
        ies.graph.serialize(destination=f"{get_uprn(record)}_ll.ttl", format="turtle")
     
        return ''
    record = ies.graph.serialize(format="turtle")
    return record
