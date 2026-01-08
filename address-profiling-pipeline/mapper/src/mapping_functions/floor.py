from models.floor import Floor
from utils import get_uprn, reset_ies_graph

from .epc_assessment import bind_and_get_epc_assessment
from .structure_unit import bind_and_get_structure_unit


def floor_function(record: dict, ies, debug_mode=False):
    """
    Creates a graph serialized to n-triples containing details about the floors of a property.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The RDF graph serialized into n-triples containing details about the floors of a property.
    """

    # only add more detail if the certificate is related to a domestic property
    if record["CertificateType"] == "domestic":
        uprn = get_uprn(record)
        structure_unit = bind_and_get_structure_unit(record, ies)
        epc_assessment = bind_and_get_epc_assessment(record, structure_unit, ies)

        reset_ies_graph(ies)
        Floor(ies, record, structure_unit.state_uri, epc_assessment.uri)

        if debug_mode:
            ies.graph.serialize(destination=f"{uprn}_floor.ttl", format="turtle")
            return

        return ies.graph.serialize(format="nt")
    return None
