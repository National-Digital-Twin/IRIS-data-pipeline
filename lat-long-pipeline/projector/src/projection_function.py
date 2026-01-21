from sqlalchemy import text
from sqlalchemy.engine import Connection

EXISTING_BUILDING_RECORD_QUERY = """
    SELECT * FROM iris.building WHERE uprn = :uprn;
"""

INSERT_BUILDING_RECORD_QUERY = """
    INSERT INTO iris.building(
        uprn, toid, first_line_of_address, post_code, point, is_residential
    )
    VALUES
    (
        :uprn,
        :toid,
        :first_line_of_address,
        :post_code,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
        true
    );
"""


def project_func(connection: Connection, record: dict):
    uprn = record["UPRN"]

    existing_building_record_result = connection.execute(
        text(EXISTING_BUILDING_RECORD_QUERY), {"uprn": uprn}
    )

    if int(existing_building_record_result.rowcount) == 0:
        connection.execute(
            text(INSERT_BUILDING_RECORD_QUERY),
            {
                "uprn": uprn,
                "toid": record["TOID"],
                "first_line_of_address": record["Address"],
                "post_code": record["Postcode"],
                "longitude": float(record["Longitude"]),
                "latitude": float(record["Latitude"]),
            },
        )
