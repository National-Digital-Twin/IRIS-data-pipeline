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
import hashlib
import geohash_tools as gh

DEBUG_MODE = False  # change to False when using with core

# declare namespaces
ies_ns = "http://ies.data.gov.uk/ontology/ies4#"
rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
ndt_ns = "http://nationaldigitaltwin.gov.uk/ontology#"
data_ns = "http://nationaldigitaltwin.gov.uk/data#"
geoplace_ns = "https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn#"

# declare local class extensions we will use
Building = ndt_ns + "Building"
Uprn = geoplace_ns + "UniquePropertyReferenceNumber"


def create_deterministic_uri_full_hash(value, type, namespace):
    full_hash = hashlib.sha256(value.encode()).hexdigest()
    lower_case_type = type.lower()
    return f"{namespace}{lower_case_type}_{full_hash}"


ies = ies_tool.IESTool(data_ns)

def add_geographic_mapping(item):
    lat = str(item.get("Latitude"))
    lon = str(item.get("Longitude"))

    my_hash = str(gh.encode(float(lat), float(lon), precision=11))
    gp = ies.instantiate(uri="http://geohash.org/" + my_hash)
    ies.add_to_graph(gp.uri, rdf_ns+"type", ies_ns + "GeoPoint")

    latitude = ies.instantiate(uri=f"http://geohash.org/{my_hash}_LAT")
    ies.add_to_graph(latitude.uri, rdf_ns+"type", f"{ies_ns}Latitude")

    longitude = ies.instantiate(uri=f"http://geohash.org/{my_hash}_LON")
    ies.add_to_graph(longitude.uri, rdf_ns+"type", f"{ies_ns}Longitude")
    
    ies.add_to_graph(subject=gp.uri, predicate=ies_ns + "isIdentifiedBy", obj=longitude)
    ies.add_to_graph(subject=gp.uri, predicate=ies_ns + "isIdentifiedBy", obj=latitude)

    ies.add_to_graph(
        subject=latitude.uri,
        predicate=f"{ies_ns}representationValue",
        obj=lat,
        is_literal=True,
        literal_type="float",
    )
    ies.add_to_graph(
        subject=longitude.uri,
        predicate=f"{ies_ns}representationValue",
        obj=lon,
        is_literal=True,
        literal_type="float",
    )
    return gp


def map_func(item):
    ies.clear_graph()
    # first our namespaces
    ies.graph.namespace_manager.bind("ies", ies_ns)
    ies.graph.namespace_manager.bind("geoplace", geoplace_ns)
    ies.graph.namespace_manager.bind("data", data_ns)
    ies.graph.namespace_manager.bind("ndt", ndt_ns)

    building_uprn = item["UPRN"].replace(".0", "")
    building_uri = f"{data_ns}building_{building_uprn}"
    toid = item["TOID"]

    shares_toid = False
    if str(item["SharesTOID"]) == "True": 
        shares_toid = True

    building = ies.instantiate(
        uri=building_uri, instance_uri_context=building_uri,
    )
    
    gp = add_geographic_mapping(item)
    ies.add_to_graph(subject=building_uri, predicate=f"{ies_ns}inLocation", obj=gp)
    
    ies_tool.ExchangedItem.add_identifier(
        building,
        building_uprn,
        id_class=Uprn,
        uri=f"{data_ns}uprn_{building_uprn}"
    )

    address_value = item["Address"]
    postcode_value = item["PostcodeLocator"]
    building.add_telicent_primary_name(address_value)

    address = ies.instantiate(
        uri=create_deterministic_uri_full_hash(address_value, "Address", data_ns)
    )
    address.add_telicent_primary_name(address_value + ", " + postcode_value)

    ies_tool.ExchangedItem.add_identifier(  
        address,
        address_value,
        id_class=ies_ns + "FirstLineOfAddress",
        uri= create_deterministic_uri_full_hash(
            "".join(address_value.replace(",", "").split()).lower(), 
            "FirstLineOfAddress", 
            data_ns
        )
    )
    
    ies.add_to_graph(building_uri, ies_ns + "inLocation", address)

    ies_tool.ExchangedItem.add_identifier(
        address,
        postcode_value,
        id_class=ies_ns + "PostalCode",
        uri= create_deterministic_uri_full_hash(
            "".join(postcode_value.split()).lower(),
            "Postcode",
            data_ns
        )
    )
    
    building_with_toid_uri = ies.instantiate(uri=building_uri, instance_uri_context=f'{data_ns}BUILDING_TOID_{str(toid)}')
    if shares_toid == True:
        print("parent")
        ies.add_to_graph(building_uri, ies_ns + "isPartOf", building_with_toid_uri)
    ies_tool.ExchangedItem.add_identifier(
        building_with_toid_uri, toid, id_class=f"{ies_ns}TOID", uri=f"{data_ns}toid_{toid}"
    )

    if DEBUG_MODE:
        ies.graph.serialize(destination=f"{building_uprn}_ll.ttl", format="turtle")
     
        return
    record = ies.graph.serialize(format="turtle")
    return record
