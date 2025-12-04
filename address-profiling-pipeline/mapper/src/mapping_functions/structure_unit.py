from models.structure_unit import StructureUnit
from utils import (
    add_ies_building_type_mappings,
    build_ies_uri,
    create_record_uri,
    get_uprn,
)


def _add_building_mapping(record: dict, ies) -> str:
    """
    Adds the common mapping for a Building entity.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The building URI.
    """
    building_uri = create_record_uri(record, "Building")
    add_ies_building_type_mappings(ies, building_uri, ["Building"])
    ies.add_triple(
        building_uri, build_ies_uri("inLocation"), create_record_uri(record, "Location")
    )
    return building_uri


def bind_and_get_structure_unit(record: dict, ies) -> StructureUnit:
    building_uri = _add_building_mapping(record, ies)
    return StructureUnit(ies, record, building_uri)


def structure_unit_function(record: dict, ies, debug_mode=False):
    """
    Creates a graph serialized to n-triples for the structure unit of a property.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The RDF graph serialized into n triples for the structure unit of a property.
    """

    uprn = get_uprn(record)
    bind_and_get_structure_unit(record, ies)

    if debug_mode:
        ies.graph.serialize(destination=f"{uprn}_structure_unit.ttl", format="turtle")
        return

    return ies.graph.serialize(format="nt")
