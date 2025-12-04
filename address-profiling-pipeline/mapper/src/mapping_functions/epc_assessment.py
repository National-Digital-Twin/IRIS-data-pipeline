from models.epc_assessment import EpcAssessment
from models.structure_unit import StructureUnit
from utils import get_uprn, reset_ies_graph

from .structure_unit import bind_and_get_structure_unit


def bind_and_get_epc_assessment(
    record: dict, structure_unit: StructureUnit, ies
) -> EpcAssessment:
    return EpcAssessment(ies, record, structure_unit)


def epc_assessment_function(record: dict, ies, debug_mode=False):
    """
    Creates a graph serialized to n-triples for the EPC assessment of a property.

    Args:
        record (dict): A record representing a building.

    Returns:
        str: The RDF graph serialized into n-triples for the EPC assessment of a property.
    """

    # only add more detail if the certificate is related to a domestic property
    if record["CertificateType"] == "domestic":
        uprn = get_uprn(record)
        structure_unit = bind_and_get_structure_unit(record, ies)

        reset_ies_graph(ies)
        bind_and_get_epc_assessment(record, structure_unit, ies)

        if debug_mode:
            ies.graph.serialize(
                destination=f"{uprn}_epc_assessment.ttl", format="turtle"
            )
            return

        return ies.graph.serialize(format="nt")
    return None
