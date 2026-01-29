# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from datetime import datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.engine import Connection

BUILDING_RECORD_EXISTS_QUERY = """
    SELECT * FROM iris.building WHERE uprn = :uprn;
"""

EPC_ASSESSMENT_RECORD_EXISTS_QUERY = """
    SELECT * FROM iris.epc_assessment WHERE uprn = :uprn AND lodgement_date = :lodgement_date AND epc_rating = :epc_rating;
"""

EPC_ASSESSMENT_ID_EXISTS_QUERY = """
    SELECT * FROM iris.epc_assessment WHERE id = :id;
"""

INSERT_EPC_ASSESSMENT_RECORD_QUERY = """
    INSERT INTO iris.epc_assessment(
        id,
        uprn,
        epc_rating,
        lodgement_date,
        sap_rating,
        expiry_date
    )
    VALUES
    (
        :id,
        :uprn,
        :epc_rating,
        :lodgement_date,
        :sap_rating,
        :expiry_date
    );
"""

INSERT_STRUCTURE_UNIT_RECORD_QUERY = """
    INSERT INTO iris.structure_unit(
        epc_assessment_id,
        type,
        built_form,
        fuel_type,
        window_glazing,
        wall_construction,
        wall_insulation,
        roof_construction,
        roof_insulation,
        roof_insulation_thickness,
        floor_construction,
        floor_insulation
    )
    VALUES
    (
        :epc_assessment_id,
        :type,
        :built_form,
        :fuel_type,
        :window_glazing,
        :wall_construction,
        :wall_insulation,
        :roof_construction,
        :roof_insulation,
        :roof_insulation_thickness,
        :floor_construction,
        :floor_insulation
    );
"""

FLOOR_CONSTRUCTION_TYPE_MAP: dict = {
    "Solid": "Solid",
    "Suspended": "Suspended",
    "AnotherDwellingBelow": "AnotherDwellingBelow",
    "OtherPremisesBelow": "OtherPremisesBelow",
    "NULL": None,
}

FLOOR_INSULATION_TYPE_MAP: dict = {
    "InsulatedFloor": "InsulatedFloor",
    "LimitedFloorInsulation": "LimitedFloorInsulation",
    "NoInsulationInFloor": "NoInsulationInFloor",
    "NULL": None,
}

FUEL_TYPE_MAP: dict = {
    "Anthracite": "Anthracite",
    "Fuel": "Fuel",
    "Biomass": "Biomass",
    "Coal": "Coal",
    "Electricity": "Electricity",
    "LPG": "LPG",
    "NaturalFuelGas": "NaturalFuelGas",
    "Oil": "Oil",
    "SmokelessCoal": "SmokelessCoal",
    "WoodChips": "WoodChips",
    "WoodLogs": "WoodLogs",
    "WoodPellets": "WoodPellets",
    "NULL": None,
}

ROOF_CONSTRUCTION_TYPE_MAP = {
    "FlatRoof": "FlatRoof",
    "AnotherDwellingAbove": "AnotherDwellingAbove",
    "OtherPremisesAbove": "OtherPremisesAbove",
    "PitchedRoof": "PitchedRoof",
    "ThatchedRoof": "ThatchedRoof",
    "RoofRooms": "RoofRooms",
    "NULL": None,
}

ROOF_INSULATION_TYPE_MAP = {
    "InsulatedAtRafters": "InsulatedAtRafters",
    "CeilingInsulated": "CeilingInsulated",
    "FlatRoofInsulation": "FlatRoofInsulation",
    "ThatchedWithAdditionalInsulation": "ThatchedWithAdditionalInsulation",
    "InsulatedWithThatched": "InsulatedWithThatched",
    "LimitedInsulationAssumed": "LimitedInsulationAssumed",
    "LimitedInsulation": "LimitedInsulation",
    "InsulatedAssumed": "InsulatedAssumed",
    "Insulated": "Insulated",
    "LoftInsulationAssumed": "LoftInsulationAssumed",
    "LoftInsulation": "LoftInsulation",
    "NoInsulationAssumedInRoof": "NoInsulationAssumedInRoof",
    "NoInsulationInRoof": "NoInsulationInRoof",
    "NULL": None,
}

WALL_CONSTRUCTION_TYPE_MAP = {
    "CavityWall": "CavityWall",
    "Cob": "Cob",
    "GraniteOrWhinstone": "GraniteOrWhinstone",
    "ParkHomeWall": "ParkHomeWall",
    "Sandstone": "Sandstone",
    "SolidBrick": "SolidBrick",
    "SystemBuilt": "SystemBuilt",
    "TimberFrame": "TimberFrame",
    "Other": "Wall",
    "NULL": None,
}

WALL_INSULATION_TYPE_MAP = {
    "InternalInsulation": "InternalInsulation",
    "ExternalInsulation": "ExternalInsulation",
    "InsulatedWall": "InsulatedWall",
    "PartialInsulation": "PartialInsulation",
    "NoInsulationInWall": "NoInsulationInWall",
    "WallInsulation": "WallInsulation",
    "NULL": None,
}


def get_expiry_date(lodgement_date: str):
    date_format = "%Y-%m-%d"
    date = datetime.strptime(lodgement_date, date_format)
    return datetime.strftime(date + relativedelta(years=+10), date_format)


def get_nullable_value(value: str):
    if value == "":
        return None
    else:
        return value


def project_func(connection: Connection, records: [dict]):
    records_to_insert = []
    records_to_insert_seen = set()

    for record in records:
        uprn = record["UPRN"]

        building_record_exists_result = connection.execute(
            text(BUILDING_RECORD_EXISTS_QUERY), {"uprn": uprn}
        )

        if int(building_record_exists_result.rowcount) == 1:
            lodgement_date = record["LodgementDate"]
            epc_rating = record["SAPBand"]
            epc_assessment_record_exists_result = connection.execute(
                text(EPC_ASSESSMENT_RECORD_EXISTS_QUERY),
                {
                    "uprn": uprn,
                    "lodgement_date": lodgement_date,
                    "epc_rating": epc_rating,
                },
            )

            if int(epc_assessment_record_exists_result.rowcount) == 0:
                record_foot_print = f"{uprn}|{epc_rating}|{lodgement_date}"

                if record_foot_print in records_to_insert_seen:
                    continue

                records_to_insert_seen.add(record_foot_print)
                records_to_insert.append(record)

    epc_assessment_records_params = []
    structure_unit_records_params = []

    for record_to_insert in records_to_insert:
        epc_assessment_id = str(uuid4())

        epc_assessment_id_record_result = connection.execute(
            text(EPC_ASSESSMENT_ID_EXISTS_QUERY), {"id": epc_assessment_id}
        )

        while int(epc_assessment_id_record_result.rowcount) == 1:
            epc_assessment_id = str(uuid4())
            epc_assessment_id_record_result = connection.execute(
                text(EPC_ASSESSMENT_ID_EXISTS_QUERY), {"id": epc_assessment_id}
            )

        lodgement_date = record_to_insert["LodgementDate"]
        epc_assessment_records_params.append(
            {
                "id": epc_assessment_id,
                "uprn": record_to_insert["UPRN"],
                "epc_rating": record_to_insert["SAPBand"],
                "lodgement_date": lodgement_date,
                "sap_rating": record_to_insert["SAPRating"],
                "expiry_date": get_expiry_date(lodgement_date),
            }
        )
        structure_unit_records_params.append(
            {
                "epc_assessment_id": epc_assessment_id,
                "type": get_nullable_value(record_to_insert["PropertyType"]),
                "built_form": get_nullable_value(record_to_insert["BuiltForm"]),
                "fuel_type": get_nullable_value(
                    FUEL_TYPE_MAP.get(record_to_insert["MainFuelType"])
                ),
                "window_glazing": get_nullable_value(
                    record_to_insert["MultipleGlazingType"]
                ),
                "wall_construction": get_nullable_value(
                    WALL_CONSTRUCTION_TYPE_MAP.get(record_to_insert["WallConstruction"])
                ),
                "wall_insulation": get_nullable_value(
                    WALL_INSULATION_TYPE_MAP.get(record_to_insert["WallInsulationType"])
                ),
                "roof_construction": get_nullable_value(
                    ROOF_CONSTRUCTION_TYPE_MAP.get(record_to_insert["RoofConstruction"])
                ),
                "roof_insulation": get_nullable_value(
                    ROOF_INSULATION_TYPE_MAP.get(
                        record_to_insert["RoofInsulationLocation"]
                    )
                ),
                "roof_insulation_thickness": get_nullable_value(
                    record_to_insert["RoofInsulationThickness"]
                ),
                "floor_construction": get_nullable_value(
                    FLOOR_CONSTRUCTION_TYPE_MAP.get(
                        record_to_insert["FloorConstruction"]
                    )
                ),
                "floor_insulation": get_nullable_value(
                    FLOOR_INSULATION_TYPE_MAP.get(record_to_insert["FloorInsulation"])
                ),
            }
        )

    connection.execute(
        text(INSERT_EPC_ASSESSMENT_RECORD_QUERY), epc_assessment_records_params
    )
    connection.execute(
        text(INSERT_STRUCTURE_UNIT_RECORD_QUERY), structure_unit_records_params
    )
