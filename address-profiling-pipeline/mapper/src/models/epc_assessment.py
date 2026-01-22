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

from ies_tool.ies_tool import IESTool
from namespaces import data_ns, iso8601_ns
from models.structure_unit import StructureUnit
from utils import (create_record_uri,
                   create_stateful_record_uri, 
                   add_ies_building_type_mappings, 
                   build_ies_building_uri, 
                   build_uri, 
                   build_ies_uri, 
                   add_ies_type_mappings, 
                   add_state_mappings,
                   add_part_mappings,
                   add_bnode_with_ies_type_and_value,
                   add_attribute_of_state_mapping
                   )
from rdflib import BNode, Literal, URIRef
from ies_tool.ies_tool import IESTool, RDF_TYPE, XSD


class EpcAssessment:
    """
    A class representing an `EpcAssessment`(s) that asseses a `StructureUnitState`.
    
    Attributes:
        uri (str): The URI of the `EpcAssessment`
    """
    uri: str = ""
    
    def __init__(self, ies: IESTool, record: dict, structure_unit: StructureUnit):
        """
        Initializes the `EpcAssessment` class and adds the common mapping as well as a mapping for the result of the
        assessment and the certificate that is produced as a result. It also adds mapping for the metrics of both SAP 
        rating and environmental impact rating.
        
        Args:
            ies (IESTool): An instance of the IES Tool, providing utility methods for mapping against the IES ontology.
            record (dict): A record representing a building.
            structure_unit (StructureUnit): An instance of `StructureUnit`, including the state of the structure unit at 
                the time of the assessment.
        """
        self.ies = ies
        self.add_epc_assessment_mapping(record, structure_unit.state_uri)
        self.add_epc_assessment_result_mapping(record)
        self.add_epc_certificate_mapping(record)
        self.add_address_match_assessment(record)
        sap_rating_uri = self.add_epc_metric(record, "SAPRating", "SAPRatingValue")
        self.add_epc_metric_calculation(record, "SAPRatingCalculation", sap_rating_uri, structure_unit)
        environmental_impact_rating_uri = self.add_epc_metric(record, "EnvironmentalImpactRating", "EnvironmentalImpactRatingValue")
        self.add_epc_metric_calculation(record, "EnvironmentalImpactRatingCalculation", environmental_impact_rating_uri, structure_unit)

    def add_epc_assessment_mapping(self, record: dict, structure_unit_state_uri: str) -> None:
        """
        Adds the core EPC assessment mapping, including its relationship to the `StructureUnitState`.
        
        Args:
            record (dict): A record representing a building.
            structure_unit_state_uri (str):  The URI of the building's structure unit state at the tme of the EPC assessment.
        
        Returns:
            None
        """
        self.uri = create_stateful_record_uri(record, "EPCAssessment")
        add_ies_building_type_mappings(self.ies, self.uri, ["EPCAssessment"])
        self.ies.add_triple(self.uri, build_ies_building_uri("assessedStateForEnergyPerformance"), structure_unit_state_uri)

    def add_epc_assessment_result_mapping(self, record: dict) -> None:
        """
        Adds the EPC assessment result mapping, including the lodgement date.
        
        Args:
            record (dict): A record representing a building.
        
        Returns:
            None
        """
        self.epc_assessment_result_uri = create_stateful_record_uri(record, "EnergyPerformanceAssessmentResult")
        add_ies_building_type_mappings(self.ies, self.epc_assessment_result_uri, ["EnergyPerformanceAssessmentResult"])
        self.lodgement_date_uri = build_uri(iso8601_ns, record.get("LodgementDate"))
        self.ies.add_triple(self.epc_assessment_result_uri, build_ies_building_uri("lodgementDate"), self.lodgement_date_uri)
        self.ies.add_triple(self.epc_assessment_result_uri, build_ies_uri("isParticipantIn"), self.uri)
        
    def add_epc_certificate_mapping(self, record: dict) -> None:
        """
        Adds the EPC assessment certificate mapping, including the SAP band and the date of creation.
        
        Args:
            record (dict): A record representing a building.
        
        Returns:
            None
        """
        sap_band = record.get("SAPBand")
        epc_certificate_uri = create_stateful_record_uri(record, "EnergyPerformanceCertificate")
        add_ies_building_type_mappings(self.ies, epc_certificate_uri, [f"UK_DOM_EPC_{sap_band}"])
        
        epc_certificate_created_uri = create_stateful_record_uri(record, "EnergyPerformanceCertificateCreated")
        add_ies_type_mappings(self.ies, epc_certificate_created_uri, ["Created"])
        add_state_mappings(self.ies, epc_certificate_created_uri, [epc_certificate_uri])  
        add_part_mappings(self.ies, epc_certificate_created_uri, [self.uri])
        self.ies.add_triple(epc_certificate_created_uri, build_ies_uri("inPeriod"), self.lodgement_date_uri)

    def add_address_match_assessment(self, record: dict) -> None:
        """
        Adds an address match assessment when a match score is available.
        """
        match_score = record.get("MatchScore")
        uprn = record.get("UPRN")
        if match_score in (None, "") or not uprn:
            return

        try:
            score_value = float(match_score)
        except (TypeError, ValueError):
            return

        assessment_uri = build_uri(data_ns, f"AddressMatchAssessment_{record['LMK_KEY']}")
        add_ies_type_mappings(self.ies, assessment_uri, ["AssessToBeTrue"])
        uprn_uri = create_record_uri(record, "UPRN")
        self.ies.add_triple(assessment_uri, build_ies_uri("assessed"), uprn_uri)
        self.ies.add_triple(
            assessment_uri, 
            build_ies_uri("confidence"), 
            str(score_value), 
            is_literal=True,
            literal_type="decimal"
        )
        self.ies.add_triple(assessment_uri, build_ies_uri("isPartOf"), self.uri)
        
    def add_epc_metric(self, record: dict, field_name: str, metric_ies_name: str) -> str:
        """
        Adds the EPC assessment certificate mapping, including the SAP band and the date of creation.
        
        Args:
            record (dict): A record representing a building.
            field_name (str): The name of the field containing the metric value within the `record` dict.
            metric_ies_name (str): The name of the metric.
        
        Returns:
            str: The URI of an EPC assessment metric.
        """
        metric_value = record.get(field_name)
        metric_bnode = add_bnode_with_ies_type_and_value(self.ies, "MeasureValue", str(int(float(metric_value))))
        characteristic_bnode = BNode()
        self.ies.graph.add((characteristic_bnode, URIRef(RDF_TYPE), URIRef(build_ies_building_uri(metric_ies_name))))
        self.ies.graph.add((characteristic_bnode, URIRef(build_ies_uri("hasValue")), metric_bnode))
        
        metric_uri = create_stateful_record_uri(record, field_name)
        add_ies_building_type_mappings(self.ies, metric_uri, [field_name])
        self.ies.graph.add((URIRef(metric_uri), URIRef(build_ies_uri("allHaveCharacteristic")), characteristic_bnode))
        return metric_uri
        
    def add_epc_metric_calculation(self, record: dict, field_name: str, metric_uri: str, structure_unit: StructureUnit) -> None:
        """
        Adds the EPC assessment certificate mapping, including the SAP band and the date of creation.
        
        Args:
            record (dict): A record representing a building.
            field_name (str): The name of the field containing the metric value within the `record` dict.
            metric_ies_name (str): The name of the metric.
            structure_unit (StructureUnit): The name of the metric.
        
        Returns:
            None
        """
        metric_calculation_uri = add_attribute_of_state_mapping(self.ies, record, field_name, [field_name], 
            [], [self.uri])
        metric_state_bnode = BNode()
        self.ies.graph.add((metric_state_bnode, URIRef(RDF_TYPE), URIRef(metric_uri)))
        self.ies.graph.add((metric_state_bnode, URIRef(build_ies_uri("isPartOf")), URIRef(structure_unit.state_uri)))
        self.ies.graph.add((metric_state_bnode, URIRef(build_ies_uri("isStateOf")), URIRef(structure_unit.uri)))
        self.ies.graph.add((URIRef(metric_calculation_uri), URIRef(build_ies_building_uri("assessedStateForEnergyPerformance")), metric_state_bnode))
