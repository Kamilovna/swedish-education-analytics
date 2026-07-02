import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv(override=True)


def get_connection():
    connection = psycopg2.connect(
        host=os.getenv("HOST"),
        port=5432,
        database=os.getenv("DATABASE"),
        user="postgres",
        password=os.getenv("PASSWORD"),
    )
    return connection


def seed_data():
    applications = pd.read_csv(
        "data/applications.csv", dtype={"municipality_code": str, "county_code": str}
    )
    applications = applications.astype(object).where(pd.notna(applications), other=None)
    con = get_connection()

    with con:
        with con.cursor() as cursor:
            for _, row in applications.iterrows():
                # --- education_area ---
                cursor.execute(
                    """
                    INSERT INTO education_area (education_area)
                    VALUES (%s)
                    ON CONFLICT (education_area) DO NOTHING;
                    """,
                    (row["education_area"],),
                )
                cursor.execute(
                    """
                    SELECT id FROM education_area WHERE education_area = %s;
                    """,
                    (row["education_area"],),
                )
                education_area_id = cursor.fetchone()[0]

                # --- education_provider ---
                cursor.execute(
                    """
                    INSERT INTO education_provider (education_provider, principal_type)
                    VALUES (%s, %s)
                    ON CONFLICT (education_provider, principal_type) DO NOTHING;
                    """,
                    (row["education_provider"], row["principal_type"]),
                )
                cursor.execute(
                    """
                    SELECT id FROM education_provider WHERE education_provider = %s AND principal_type = %s;
                    """,
                    (row["education_provider"], row["principal_type"]),
                )
                education_provider_id = cursor.fetchone()[0]

                # --- sun5 ---
                if row["sun5_code"] is not None:
                    cursor.execute(
                        """
                        INSERT INTO sun5 (sun5_code, sun5_name)
                        VALUES (%s, %s)
                        ON CONFLICT (sun5_code) DO NOTHING;
                        """,
                        (row["sun5_code"], row["sun5_name"]),
                    )

                # --- applications ---
                cursor.execute(
                    """
                    INSERT INTO applications (
                        source_year,
                        source_file,
                        source_sheet,
                        case_number,
                        education_name,
                        education_area_id,
                        decision,
                        municipality_code,
                        education_credits,
                        study_mode,
                        study_pace_percentage,
                        education_provider_id,
                        sun5_code,
                        seqf_level,
                        narrow_occupational_area,
                        total_sought_places,
                        total_granted_places,
                        is_approved,
                        is_distance,
                        program_length_years
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;
                    """,
                    (
                        row["source_year"],
                        row["source_file"],
                        row["source_sheet"],
                        row["case_number"],
                        row["education_name"],
                        education_area_id,
                        row["decision"],
                        row["municipality_code"],
                        row["education_credits"],
                        row["study_mode"],
                        row["study_pace_percentage"],
                        education_provider_id,
                        row["sun5_code"],
                        row["seqf_level"],
                        row["narrow_occupational_area"],
                        row["total_sought_places"],
                        row["total_granted_places"],
                        row["is_approved"],
                        row["is_distance"],
                        row["program_length_years"],
                    ),
                )


def create_tables():
    con = get_connection()
    create_education_area_table_query = """
    CREATE TABLE IF NOT EXISTS education_area (
        id SERIAL PRIMARY KEY,
        education_area VARCHAR(255) NOT NULL UNIQUE
        );
    """
    create_county_table_query = """
    CREATE TABLE IF NOT EXISTS county (
        county_code VARCHAR(2) PRIMARY KEY,
        county VARCHAR(255)
    );
    """
    create_municipality_table_query = """
    CREATE TABLE IF NOT EXISTS municipality (
        municipality_code VARCHAR(4) PRIMARY KEY,
        municipality VARCHAR(255),
        county_code VARCHAR(2) REFERENCES county(county_code)
    );
    """
    create_education_provider_table_query = """
    CREATE TABLE IF NOT EXISTS education_provider (
        id SERIAL PRIMARY KEY,
        education_provider VARCHAR(500) NOT NULL,
        principal_type VARCHAR(255) NOT NULL,
        UNIQUE(education_provider, principal_type)
    );
    """

    create_sun5_table_query = """
    CREATE TABLE IF NOT EXISTS sun5 (
        sun5_code VARCHAR(50) PRIMARY KEY,
        sun5_name VARCHAR(500) NOT NULL
    );
    """

    create_application_table_query = """
    CREATE TABLE IF NOT EXISTS applications (
        id SERIAL PRIMARY KEY,
        case_number VARCHAR(100) NOT NULL,
        source_year SMALLINT NOT NULL,
        source_file VARCHAR(255) NOT NULL,
        source_sheet VARCHAR(255) NOT NULL,
        education_name VARCHAR(500) NOT NULL,
        education_area_id INT REFERENCES education_area(id),
        decision VARCHAR(50) NOT NULL,
        municipality_code VARCHAR(4) REFERENCES municipality(municipality_code),
        education_credits INT NOT NULL,
        study_mode VARCHAR(50) NOT NULL,
        study_pace_percentage SMALLINT NOT NULL,
        education_provider_id INT REFERENCES education_provider(id),
        sun5_code VARCHAR(50) REFERENCES sun5(sun5_code),
        seqf_level NUMERIC(3,1),
        narrow_occupational_area BOOLEAN,
        total_sought_places INT NOT NULL,
        total_granted_places INT NOT NULL,
        is_approved BOOLEAN NOT NULL,
        is_distance BOOLEAN NOT NULL,
        program_length_years NUMERIC(4,1) NOT NULL
    );
    """
    create_population_table_query = """
    CREATE TABLE IF NOT EXISTS population (
        municipality_code VARCHAR(4) REFERENCES municipality(municipality_code),
        year SMALLINT NOT NULL,
        population INT NOT NULL,
        PRIMARY KEY (municipality_code, year)
    );
    """

    with con:
        with con.cursor() as cursor:
            cursor.execute(create_education_area_table_query)
            cursor.execute(create_county_table_query)
            cursor.execute(create_municipality_table_query)
            cursor.execute(create_education_provider_table_query)
            cursor.execute(create_sun5_table_query)
            cursor.execute(create_application_table_query)
            cursor.execute(create_population_table_query)


def seed_municipalities():
    municipalities = pd.read_csv(
        "data/municipalities.csv", dtype={"municipality_code": str, "county_code": str}
    )

    con = get_connection()

    with con:
        with con.cursor() as cursor:
            for _, row in municipalities.iterrows():
                cursor.execute(
                    """
                    INSERT INTO municipality
                    (municipality_code, municipality, county_code)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (municipality_code) DO NOTHING;
                    """,
                    (row["municipality_code"], row["municipality"], row["county_code"]),
                )


def seed_counties():
    counties = pd.read_csv("data/countys.csv", dtype={"county_code": str})

    con = get_connection()

    with con:
        with con.cursor() as cursor:
            for _, row in counties.iterrows():
                cursor.execute(
                    """
                    INSERT INTO county
                    (county_code, county)
                    VALUES (%s, %s)
                    ON CONFLICT (county_code) DO NOTHING;
                    """,
                    (row["county_code"], row["county"]),
                )


def seed_population():
    population = pd.read_csv(
        "data/population_2020-2025.csv", dtype={"municipality_code": str}
    )

    con = get_connection()

    with con:
        with con.cursor() as cursor:
            for _, row in population.iterrows():
                cursor.execute(
                    """
                    INSERT INTO population
                    (municipality_code, year, population)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (municipality_code, year) DO NOTHING;
                    """,
                    (row["municipality_code"], row["year"], row["population"]),
                )


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")

    seed_counties()
    print("Counties seeded successfully.")

    seed_municipalities()
    print("Municipalities seeded successfully.")

    seed_data()
    print("Data seeded successfully.")

    seed_population()
    print("Population seeded successfully.")
