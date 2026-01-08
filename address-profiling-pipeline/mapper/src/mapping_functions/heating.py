from models.heating_system import HeatingSystem
from utils import create_stateful_record_uri, get_uprn


def heating_function(record: dict, ies, debug_mode=False):
    """
    Creates a graph serialized to n-triples containing details about the heating system of a property.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The RDF graph serialized into n-triples containing details about the heating system of a property.
    """

    uprn = get_uprn(record)

    structure_unit_state_uri = create_stateful_record_uri(record, "StructureUnitState")

    # only add more detail if the certificate is related to a domestic property
    if record["CertificateType"] == "domestic":
        HeatingSystem(ies, record, structure_unit_state_uri)

        if debug_mode:
            ies.graph.serialize(destination=f"{uprn}_epc.ttl", format="turtle")
            return

        return ies.graph.serialize(format="nt")
    return None
