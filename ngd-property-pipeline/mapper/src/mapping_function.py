# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import ast
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

# Namespaces
ies_ns = "http://informationexchangestandard.org/ont/ies#"
ies_building_ns = "http://ies.data.gov.uk/ontology/ies-building1#"
data_ns = "http://ndtp.co.uk/data#"
qudt_ns = "http://qudt.org/schema/qudt/"
unit_ns = "http://qudt.org/vocab/unit/"
quantitykind_ns = "http://qudt.org/vocab/quantitykind/"


def _bind_namespaces(g: Graph) -> None:
    g.namespace_manager.bind("building", ies_building_ns)
    g.namespace_manager.bind("data", data_ns)
    g.namespace_manager.bind("ies", ies_ns)
    # Extra prefixes used by expected TTLs
    g.namespace_manager.bind("iso8601", "http://iso8601.iso.org/")
    g.namespace_manager.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.namespace_manager.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
    g.namespace_manager.bind("qudt", qudt_ns)
    g.namespace_manager.bind("unit", unit_ns)
    g.namespace_manager.bind("quantitykind", quantitykind_ns)


def _build_uri(ns: str, type_: str) -> str:
    return f"{ns}{type_}"


def _fmt_date_ddmmyyyy(iso_date: str) -> str:
    # iso_date is expected as YYYY-MM-DD; fallback to as-is if malformed
    try:
        y, m, d = iso_date.split("-")
        return f"{d}{m}{y}"
    except Exception:
        return iso_date


def _date_for_record(record: dict) -> str:
    # Heuristic from fixtures: if capture method is Default Value, use update date; otherwise versiondate
    capture = record.get("roofmaterial_capturemethod", "")
    date_src = record.get("versiondate")
    if capture == "Default Value":
        date_src = record.get("roofmaterial_updatedate", date_src)
    return _fmt_date_ddmmyyyy(date_src or "")


def _to_number(value: str) -> Optional[Tuple[Literal, bool]]:
    """Return Literal for numeric string; None if empty. Bool indicates integer (True) or decimal (False)."""
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        # Use Decimal to ensure xsd:decimal for non-integers
        d = Decimal(s)
        if d == d.to_integral_value():
            return Literal(int(d)), True
        return Literal(str(d), datatype=XSD.decimal), False
    except (InvalidOperation, ValueError):
        return None


def _material_class(value: str) -> str:
    mapping = {
        "Fabric": "fabric",
        "Glass or Polycarbonate": "GlassOrPolycarbonate",
        "Green Roof": "GreenRoof",
        "Metal": "metal",
        "Mixed": "MixedRoofMaterial",
        "Thatch": "thatch",
        "Tile Or Stone Or Slate": "TileOrStoneOrSlate",
        "Unknown": "UnknownRoofMaterial",
        "Other": "OtherRoofMaterial",
        "Waterproof Membrane Or Concrete": "WaterproofMembraneOrConcrete",
    }
    return mapping.get(value, value.replace(" ", ""))


def _solar_class(value: str) -> str:
    mapping = {
        "Not Present": "NoSolarPanels",
        "Present": "HasSolarPanels",
        "Unknown": "UnknownSolarPanelPresence",
    }
    return mapping.get(value, value.replace(" ", ""))


def _shape_class(value: str) -> str:
    mapping = {
        "Flat": "FlatRoofShape",
        "Pitched": "PitchedRoofShape",
        "Mixed": "MixedRoofShape",
        "Unknown": "UnknownRoofShape",
    }
    return mapping.get(value, value.replace(" ", ""))


def _add_quantity_bnode(g: Graph, number_lit: Literal) -> BNode:
    qty = BNode()
    g.add((qty, RDF.type, URIRef(_build_uri(qudt_ns, "Quantity"))))
    g.add(
        (
            qty,
            URIRef(_build_uri(qudt_ns, "hasQuantityKind")),
            URIRef(_build_uri(quantitykind_ns, "Area")),
        )
    )
    g.add((qty, URIRef(_build_uri(qudt_ns, "unit")), URIRef(_build_uri(unit_ns, "M2"))))
    g.add((qty, URIRef(_build_uri(qudt_ns, "value")), number_lit))
    return qty


def _add_surface_area_bnode(g: Graph, value_lit: Literal) -> BNode:
    surface = BNode()
    g.add((surface, RDF.type, URIRef(_build_uri(ies_building_ns, "SurfaceArea"))))
    g.add(
        (
            surface,
            URIRef(_build_uri(ies_building_ns, "hasQuantity")),
            _add_quantity_bnode(g, value_lit),
        )
    )
    return surface


def _add_aspect(
    g: Graph,
    roof_state_uri: str,
    osid: str,
    date_suffix: str,
    label: str,
    number_str: str,
) -> None:
    value = _to_number(number_str)
    if value is None:
        return  # skip if empty
    value_lit, _ = value
    aspect_type = (
        f"{label}FacingRoofSectionSum"
        if label != "AreaIndeterminable"
        else "AreaIndeterminableRoofSectionSum"
    )
    if label == "AreaIndeterminable":
        subject = _build_uri(
            data_ns, f"BuildingAreaIndeterminable_{osid}_{date_suffix}"
        )
    else:
        subject = _build_uri(
            data_ns, f"Building{label}FacingRoofSections_{osid}_{date_suffix}"
        )
    g.add((URIRef(subject), RDF.type, URIRef(_build_uri(ies_building_ns, aspect_type))))
    g.add(
        (
            URIRef(subject),
            URIRef(_build_uri(ies_ns, "isPartOf")),
            URIRef(roof_state_uri),
        )
    )
    # Attach surface area structure
    g.add(
        (
            URIRef(subject),
            URIRef(_build_uri(ies_building_ns, "hasCombinedSurfaceArea")),
            _add_surface_area_bnode(g, value_lit),
        )
    )


def _link_uprns(g: Graph, osid: str, uprnreference: str) -> None:
    try:
        entries = ast.literal_eval(uprnreference)
        for e in entries:
            uprn = e.get("uprn")
            if uprn is None:
                continue
            g.add(
                (
                    URIRef(_build_uri(data_ns, f"StructureUnit_{uprn}")),
                    URIRef(_build_uri(ies_ns, "isPartOf")),
                    URIRef(_build_uri(data_ns, f"Building_{osid}")),
                )
            )
    except Exception:
        # if malformed, do nothing
        return


def map_func(record: dict, debug_mode: str) -> str:
    """Map a single NGD building record into a Turtle RDF graph string."""
    g = Graph()
    _bind_namespaces(g)

    osid = record.get("osid")
    date_suffix = _date_for_record(record)

    building_uri = _build_uri(data_ns, f"Building_{osid}")
    g.add(
        (
            URIRef(building_uri),
            RDF.type,
            URIRef(_build_uri(ies_building_ns, "Building")),
        )
    )

    # Roof and state
    roof_uri = _build_uri(data_ns, f"BuildingRoof_{osid}")
    g.add((URIRef(roof_uri), RDF.type, URIRef(_build_uri(ies_building_ns, "Roof"))))
    g.add(
        (URIRef(roof_uri), URIRef(_build_uri(ies_ns, "isPartOf")), URIRef(building_uri))
    )

    roof_state_uri = _build_uri(data_ns, f"BuildingRoofState_{osid}_{date_suffix}")
    g.add(
        (
            URIRef(roof_state_uri),
            RDF.type,
            URIRef(_build_uri(ies_building_ns, "RoofState")),
        )
    )
    g.add(
        (
            URIRef(roof_state_uri),
            URIRef(_build_uri(ies_ns, "isStateOf")),
            URIRef(roof_uri),
        )
    )

    material_cls = _material_class(record.get("roofmaterial_primarymaterial", ""))
    g.add(
        (
            URIRef(roof_state_uri),
            URIRef(_build_uri(ies_building_ns, "isMadeOf")),
            URIRef(_build_uri(ies_building_ns, material_cls)),
        )
    )

    # Solar panel presence as a building state on the Building
    solar_state_uri = _build_uri(data_ns, f"BuildingSolarState_{osid}_{date_suffix}")
    g.add(
        (
            URIRef(solar_state_uri),
            RDF.type,
            URIRef(_build_uri(ies_building_ns, "BuildingState")),
        )
    )
    g.add(
        (
            URIRef(solar_state_uri),
            RDF.type,
            URIRef(
                _build_uri(
                    ies_building_ns,
                    _solar_class(record.get("roofmaterial_solarpanelpresence", "")),
                )
            ),
        )
    )
    g.add(
        (
            URIRef(solar_state_uri),
            URIRef(_build_uri(ies_ns, "isStateOf")),
            URIRef(building_uri),
        )
    )

    # Directional aspects and area indeterminable
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "East",
        record.get("roofshapeaspect_areafacingeast_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "North",
        record.get("roofshapeaspect_areafacingnorth_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "NorthEast",
        record.get("roofshapeaspect_areafacingnortheast_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "NorthWest",
        record.get("roofshapeaspect_areafacingnorthwest_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "South",
        record.get("roofshapeaspect_areafacingsouth_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "SouthEast",
        record.get("roofshapeaspect_areafacingsoutheast_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "SouthWest",
        record.get("roofshapeaspect_areafacingsouthwest_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "West",
        record.get("roofshapeaspect_areafacingwest_m2"),
    )
    _add_aspect(
        g,
        roof_state_uri,
        osid,
        date_suffix,
        "AreaIndeterminable",
        record.get("roofshapeaspect_areaindeterminable_m2"),
    )

    # Roof shape state on the Building
    roof_shape_uri = _build_uri(data_ns, f"BuildingRoofShape_{osid}_{date_suffix}")
    g.add(
        (
            URIRef(roof_shape_uri),
            RDF.type,
            URIRef(_build_uri(ies_building_ns, "RoofState")),
        )
    )
    g.add(
        (
            URIRef(roof_shape_uri),
            RDF.type,
            URIRef(
                _build_uri(
                    ies_building_ns,
                    _shape_class(record.get("roofshapeaspect_shape", "")),
                )
            ),
        )
    )
    g.add(
        (
            URIRef(roof_shape_uri),
            URIRef(_build_uri(ies_ns, "isStateOf")),
            URIRef(building_uri),
        )
    )

    # Link UPRNs back to building
    _link_uprns(g, osid, record.get("uprnreference", "[]"))

    if debug_mode:
        g.serialize(destination=f"{osid}_os_ngd.ttl", format="turtle")
        return ""

    return g.serialize(format="turtle")
