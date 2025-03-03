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

import ies_tool.ies_tool as ies_tool
import hashlib
import ndt_classes as ndt
from ies_tool.ies_tool import ParticularPeriod


DEBUG_MODE = False  # change to False when using with core

# declare namespaces
ies_ns = "http://ies.data.gov.uk/ontology/ies4#"
rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
# IES with uncertainty v2.0 namespace
ies_uncertainty_ns = "http://ies.data.gov.uk/ontology/ies_uncertainty_proposal/v2.0#"
ndt_ns = "http://nationaldigitaltwin.gov.uk/ontology#"
data_ns = "http://nationaldigitaltwin.gov.uk/data#"
epc_ns =  "http://gov.uk/government/organisations/department-for-levelling-up-housing-and-communities/ontology/epc#"

geoplace_ns = "https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn#"

# declare QUDT namespaces
qudt = "http://qudt.org/2.1/schema/qudt/"
qudt_unit = "http://qudt.org/2.1/vocab/unit/"
qudt_quantitykind = "http://qudt.org/2.1/vocab/quantitykind/"

Efficiency = qudt_quantitykind + "Efficiency"
SAP_Point = ndt_ns + "SAP_POINT"
Thickness = qudt_quantitykind + "Thickness"
mm = qudt_unit + "MilliM"

# declare local class extensions we will use
Building = ndt_ns + "Building"


property_type_lookup = {
    "House": ndt_ns + "House",
    "Flat": ndt_ns + "Flat",
    "Bungalow": ndt_ns + "Bungalow",
    "Maisonette": ndt_ns + "Maisonette",
    "ParkHome": ndt_ns + "ParkHome",
}

build_form_lookup = {
    "SemiDetached": ndt_ns + "SemiDetached",
    "EndTerrace": ndt_ns + "EndTerrace",
    "Detached": ndt_ns + "Detached",
    "MidTerrace": ndt_ns + "MidTerrace",
    "EnclosedEndTerrace": ndt_ns + "EnclosedEndTerrace",
    "EnclosedMidTerrace": ndt_ns + "EnclosedMidTerrace",
}

epc_rating_map = {
    "A": f"{epc_ns}BuildingWithEnergyRatingOfA",
    "B": f"{epc_ns}BuildingWithEnergyRatingOfB",
    "C": f"{epc_ns}BuildingWithEnergyRatingOfC",
    "D": f"{epc_ns}BuildingWithEnergyRatingOfD",
    "E": f"{epc_ns}BuildingWithEnergyRatingOfE",
    "F": f"{epc_ns}BuildingWithEnergyRatingOfF",
    "G": f"{epc_ns}BuildingWithEnergyRatingOfG",
}


PartOfBuilding = ndt_ns + "PartOfBuilding"
Uprn = geoplace_ns + "UniquePropertyReferenceNumber"


def create_deterministic_uri_short_hash(value, type, namespace):
    hash = hashlib.sha256(value.encode()).hexdigest()
    short_hash = hash[:16]
    lower_case_type = type.lower()
    return f"{namespace}{lower_case_type}_{short_hash}"

def add_qudt_quantity(value, unit_class, quantitykind_class, deterministic_uri_salt=""): #check
    quantity = ies.instantiate(      
        uri=create_deterministic_uri_short_hash(
            f"{str(value)}{unit_class}{quantitykind_class}{deterministic_uri_salt}", "Quantity", data_ns
        ),
    )
    ies.add_to_graph(
         quantity.uri, qudt + "hasQuantityKind", quantitykind_class)
    
    ies.add_to_graph(quantity.uri, qudt + "unit", unit_class)
    # need to handle if value is a greater than value e.g. 300+
    value_predicate = "value"
    if "+" in f"{value}": 
        value_predicate = "lowerBound"
        value = value.split("+")[0]
    
    ies.add_to_graph(subject=quantity.uri, predicate= f"{qudt}{value_predicate}", obj= f"{value}", is_literal=True, literal_type="float")
    
    return quantity

def add_fusion( fusion_of_class, part_of_string):
    Fusion = ndt_ns + "Fusion"
    fusedInto = ndt_ns + "fusedInto"

    # we create a subclass of the fusion_of_class 
    # that only has those things that we want to fuse as members
    fusion_of_class_string = fusion_of_class.split('#')[1]
    set_of_things_to_fuse_string = f"{fusion_of_class_string}At{part_of_string}"
    set_of_things_to_fuse = data_ns + set_of_things_to_fuse_string
    ies.add_to_graph(set_of_things_to_fuse, rdfs_ns+"subClassOf", fusion_of_class)

    fusion = ies.instantiate(uri=f"{data_ns}{set_of_things_to_fuse_string.lower()}_fusion")
    
    ies.add_to_graph(set_of_things_to_fuse, fusedInto, fusion.uri)
    return fusion

def add_insulatable_fusion(thing_class, building_uprn, thing_insulation_class=None, ndt_formated_thickness = None):
    thing_fusion = add_fusion(
        thing_class, 
        building_uprn
    )
    if thing_insulation_class:
        thing_insulation_fusion = add_fusion(      
            thing_insulation_class,
            building_uprn
        )
        thing_insulation_thickness = parse_insultation_thickness(ndt_formated_thickness)
        if thing_insulation_thickness:
            thing_insulation_quantity = add_qudt_quantity(thing_insulation_thickness, mm, Thickness, building_uprn)
            ies.add_to_graph( thing_insulation_fusion.uri, ies_ns+"hasCharacteristic", thing_insulation_quantity.uri)
        ies.add_to_graph(thing_insulation_fusion.uri, ies_ns+"isPartOf", thing_fusion.uri)
    return thing_fusion


def parse_insultation_thickness(thickness_string):
    if "mm" not in thickness_string: return None
    return thickness_string.split("mm")[0]

ies = ies_tool.IESTool(data_ns)

def map_func(item):
    ies.clear_graph()
    # first our namespaces
    ies.graph.namespace_manager.bind("ies", ies_ns)
    ies.graph.namespace_manager.bind("data", data_ns)
    ies.graph.namespace_manager.bind("iesuncertainty", ies_uncertainty_ns)
    ies.graph.namespace_manager.bind("ndt", ndt_ns)
    ies.graph.namespace_manager.bind("epc", epc_ns)
    ies.graph.namespace_manager.bind("geoplace", geoplace_ns)
    ies.graph.namespace_manager.bind("qudt", qudt)
    ies.graph.namespace_manager.bind("unit", qudt_unit)
    ies.graph.namespace_manager.bind("quantitykind", qudt_quantitykind)

    # build the primary object, the building
    building_object = item
    # replace incase UPRN is made a float by excel
    building_uprn = building_object["UPRN"].replace(".0", "")
    building_uri = f"{data_ns}building_{building_uprn}"
    building_type_literal = building_object.get("PropertyType", "Building")
    building_type = property_type_lookup.get(building_type_literal, Building)
    building = ies.instantiate(
        uri=building_uri
    )
    ies.add_to_graph(building.uri, rdf_ns+"type", building_type)

    # first we build the actual world graph of the building..
    ies_tool.ExchangedItem.add_identifier(
        building,
        building_uprn,
        id_class=Uprn,
        uri=f"{data_ns}uprn_{building_uprn}"),
    
    # address_value = building_object["Address"]
    # postcode_value = building_object["Postcode"]
    # ies.add_telicent_primary_name(building, building_type_literal + " at " + address_value)

    # address = ies.instantiate(
    #     ies_ns+"Address",
    #     instance= create_deterministic_uri_short_hash(address_value, "Address", data_ns)
    # )
    # ies.add_telicent_primary_name(address, address_value + ", " + postcode_value)

    # ies.add_identifier(  
    #     address,
    #     address_value,
    #     _class=ies_ns + "FirstLineOfAddress",
    #     id_uri= create_deterministic_uri_short_hash(
    #         "".join(address_value.replace(",", "").split()).lower(), 
    #         "FirstLineOfAddress", 
    #         data_ns
    #     )
    # )
    
    # ies.add_to_graph(building, ies_ns + "inLocation", address)
    # ies.add_identifier(
    #     address,
    #     postcode_value,
    #     _class=ies_ns + "PostalCode",
    #     id_uri= create_deterministic_uri_short_hash(
    #         "".join(postcode_value.split()).lower(),
    #         "Postcode",
    #         data_ns
    #     )
    # )
    # only add more detail if the certificate is related to a domestic property
    if building_object["CertificateType"] == "domestic":
        roof_class = ndt.roof_type_map.get(building_object["RoofConstruction"], None)
        built_form_type = building_object.get("BuiltForm", None)
        if built_form_type:
            ies.instantiate(uri=build_form_lookup[built_form_type.replace("-", "")], instance_uri_context=building_uri)
            
        # add state with EPC and SAP info associated to when it was inspected
        current_epc_rating = building_object["SAPBand"]
        state_id = building_object["LMK_KEY"]
        building_inspection_date = building_object["LodgementDate"] # taken from the filename of the data source
        
        
        # the building inspection state should not be instantiated, as we do not want it to be an RdfsResource
        building_inspection_state_uri = data_ns + "state_" + state_id
        ies.add_to_graph(building_inspection_state_uri, rdf_ns+"type", epc_rating_map[current_epc_rating])
        ies.add_to_graph(building_inspection_state_uri, ies_ns+"isStateOf", building)
        pp_instance = ParticularPeriod(tool=ies, time_string=building_inspection_date)
        ies.add_triple(building_inspection_state_uri, f"{ies_ns}inPeriod", pp_instance._uri)

        current_sap_points = int(float(building_object["SAPRating"]))
        current_sap_points_qudt = add_qudt_quantity(
            current_sap_points, 
            Efficiency, 
            SAP_Point,
            building_uprn,
        )
        ies.add_to_graph(building_inspection_state_uri, ies_ns+"hasCharacteristic", current_sap_points_qudt)

        # now add the parts of the building as fusions
        # walls
        wall_class = ndt.wall_type_map.get(building_object["WallConstruction"], None)
        if wall_class:
            wall_class_uri = ndt_ns + wall_class
            ies.add_to_graph( wall_class_uri, rdfs_ns+"subClassOf", ndt_ns + "Wall")
            wall_insulation_class = ndt.wall_insulation_map.get(building_object["WallInsulationType"], None)
            if wall_insulation_class:
                wall_insulation_class = ndt_ns + wall_insulation_class
            wall_fusion = add_insulatable_fusion(
                wall_class_uri, 
                building_uprn,
                wall_insulation_class, 
                building_object.get("WallInsulationThickness", None),
            )
            ies.add_to_graph(wall_fusion.uri, ies_ns+"isPartOf", building_inspection_state_uri)

        # floors
        floor_class = ndt.floor_type_map.get(building_object["FloorConstruction"], None)
        if floor_class:
            floor_class_uri = ndt_ns + floor_class
            ies.add_to_graph( floor_class_uri, rdfs_ns+"subClassOf", ndt_ns + "Floor")
            floor_insulation_class = ndt.floor_insulation_map.get(building_object["FloorInsulation"], None)
            if floor_insulation_class:
                floor_insulation_class = ndt_ns + floor_insulation_class
            floor_fusion = add_insulatable_fusion(
                floor_class_uri, 
                building_uprn,
                floor_insulation_class,
                building_object.get("FloorInsulationThickness", None),
            )
            ies.add_to_graph(floor_fusion.uri, ies_ns+"isPartOf", building_inspection_state_uri)

        # roofs
        roof_class = ndt.roof_type_map.get(building_object["RoofConstruction"], None)
        if roof_class:
            roof_class_uri = ndt_ns + roof_class
            ies.add_to_graph( roof_class_uri, rdfs_ns+"subClassOf", ndt_ns + "Roof")
            roof_insulation_class = ndt.roof_insulation_map.get(building_object["RoofInsulationLocation"], None)
            if roof_insulation_class:
                roof_insulation_class = ndt_ns + roof_insulation_class
            roof_fusion = add_insulatable_fusion(     
                roof_class_uri, 
                building_uprn,
                roof_insulation_class, 
                building_object.get("RoofInsulationThickness", None),
            )
            ies.add_to_graph(roof_fusion.uri, ies_ns+"isPartOf", building_inspection_state_uri)

        # windows
        window_class = ndt.window_type_map.get(building_object["MultipleGlazingType"], None)
        if window_class:
            window_class_uri = ndt_ns + window_class
            ies.add_to_graph( window_class_uri, rdfs_ns+"subClassOf", ndt_ns + "Window")
            window_fusion = add_fusion(
                window_class_uri, 
                building_uprn
            )
            ies.add_to_graph(window_fusion.uri, ies_ns+"isPartOf", building_inspection_state_uri)

    if DEBUG_MODE:
        ies.graph.serialize(destination=f"{building_uprn}_epc.ttl", format="turtle")
        return
    record = ies.graph.serialize(format="nt")
    return record


if DEBUG_MODE:
    test_item = {
        "LMK_KEY": "906585679502013033118433406677898",
        "UPRN": "100032149557",
        "UDPRN": "",
        "ndtAddressId": "",
        "Address": "78, High Street, Wootton Bridge, Ryde, PO33 4PR",
        "Postcode": "PO33 4PR",
        "EnvironmentalImpactRating": "47.0",
        "EnvironmentalImpactRatingBand": "",
        "FuelBills(£/yr)": "",
        "RealisticFuelBill(Regional)": "",
        "tCO2": "3.9",
        "HeatingCost(£/yr)": "696.0",
        "SAPRating": "49.0",
        "SAPBand": "E",
        "LodgementDate": "2013-03-31",
        "SAPVersion": "",
        "PropertyType": "Bungalow",
        "ConstructionAgeBand": "1900-1929",
        "BuiltForm": "Detached",
        "StoreysCount": "",
        "FlatLocation": "",
        "FlatLevel": "",
        "LowestFloorArea": "",
        "MainHeatingCategory": "BoilerRadiatorsMainsGas",
        "MainFuelType": "MainsGas",
        "MainHeatingControl": "2107",
        "DerivedSAPMainHeatingCode": "",
        "HeatEmitterType": "",
        "WaterHeatingFuel": "",
        "RoofConstruction": "Pitched",
        "RoofInsulationLocation": "LoftInsulation",
        "RoofInsulationThickness": "25mm",
        "WallConstruction": "CavityWall",
        "WallInsulationType": "NoInsulation",
        "WallInsulationThickness": "",
        "FloorConstruction": "Suspended",
        "FloorInsulation": "Insulated",
        "FloorInsulationThickness": "",
        "MultipleGlazingType": "DoubleGlazingAfter2002",
        "OpenFireplacesCount": "0.0",
        "Renewables": "0.0",
        "Ventilation": "Natural",
        "WaterHeatingCost(£/yr)": "84.0",
        "LightingCost(£/yr)": "59.0",
        "TotalFloorArea": "58.0",
        "FuzzyMatched": "0",
        "CertificateType": "domestic"
    }

    mapped = map_func(test_item)
