# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from datetime import datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.engine import Connection

INSERT_EPC_ASSESSMENT_RECORD_QUERY = """
    INSERT INTO iris.stg_epc_assessment(
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
    INSERT INTO iris.stg_structure_unit(
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


def project_func(connection: Connection, record: dict):
    uprn = record["UPRN"]
    lodgement_date = record["LodgementDate"]
    epc_rating = record["SAPBand"]
    epc_assessment_id = uuid4()

    epc_assessment_record_params = {
        "id": str(epc_assessment_id),
        "uprn": uprn,
        "epc_rating": epc_rating,
        "lodgement_date": lodgement_date,
        "sap_rating": record["SAPRating"],
        "expiry_date": get_expiry_date(lodgement_date),
    }
    structure_unit_record_params = {
        "epc_assessment_id": str(epc_assessment_id),
        "type": get_nullable_value(record["PropertyType"]),
        "built_form": get_nullable_value(record["BuiltForm"]),
        "fuel_type": get_nullable_value(FUEL_TYPE_MAP.get(record["MainFuelType"])),
        "window_glazing": get_nullable_value(record["MultipleGlazingType"]),
        "wall_construction": get_nullable_value(
            WALL_CONSTRUCTION_TYPE_MAP.get(record["WallConstruction"])
        ),
        "wall_insulation": get_nullable_value(
            WALL_INSULATION_TYPE_MAP.get(record["WallInsulationType"])
        ),
        "roof_construction": get_nullable_value(
            ROOF_CONSTRUCTION_TYPE_MAP.get(record["RoofConstruction"])
        ),
        "roof_insulation": get_nullable_value(
            ROOF_INSULATION_TYPE_MAP.get(record["RoofInsulationLocation"])
        ),
        "roof_insulation_thickness": get_nullable_value(
            record["RoofInsulationThickness"]
        ),
        "floor_construction": get_nullable_value(
            FLOOR_CONSTRUCTION_TYPE_MAP.get(record["FloorConstruction"])
        ),
        "floor_insulation": get_nullable_value(
            FLOOR_INSULATION_TYPE_MAP.get(record["FloorInsulation"])
        ),
    }

    connection.execute(
        text(INSERT_EPC_ASSESSMENT_RECORD_QUERY), epc_assessment_record_params
    )
    connection.execute(
        text(INSERT_STRUCTURE_UNIT_RECORD_QUERY), structure_unit_record_params
    )
