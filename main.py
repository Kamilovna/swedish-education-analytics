from fastapi import FastAPI, Query
from psycopg2.extras import RealDictCursor
from setup import get_connection
from schemas import (
    YearEnum,
    CountyEnum,
    FormatEnum,
    EducationAreaEnum,
    Application,
    StatisticsEducationArea,
    StatisticsProvider,
    PrincipalTypeEnum,
    StatisticsSun5,
    YearEnumSun,
)
from fastapi.responses import StreamingResponse
import csv
import io

app = FastAPI(
    title="Applications API",
    description="API for retrieving data about applications for vocational education",
    version="1.0.0",
)


@app.get(
    "/applications",
    summary="Get all applications with filters",
    description="""
*Returns a list of applications for vocational education.*

**Allowed parameters:**

- `year` - Year of the applications

- `county` - Filter by county

- `municipality` - Filter by municipality

- `is_approved` - Filter by approved or non-approved applications

- `education_provider` - Filter by provider

- `limit` - Limits the number of applications returned

""",
    response_description="List of applications for vocational education",
    response_model=list[Application],
)
async def list_applications(
    format: FormatEnum = Query(
        default=FormatEnum.json,
        description="json or csv",
    ),
    limit: int = Query(
        default=10,
        description="Limits the number of applications returned",
        ge=1,
        le=100,
    ),
    year: YearEnum | None = Query(
        default=None,
        description="Year of the applications",
    ),
    county: CountyEnum | None = Query(
        default=None,
        description="Filter by county",
    ),
    is_approved: bool | None = Query(
        default=None,
        description="Filter by approved or non-approved applications",
    ),
    education_provider: str | None = Query(
        default=None,
        description="Filter by provider",
    ),
    municipality: str | None = Query(
        default=None,
        description="Filter by municipality",
    ),
    is_distance: bool | None = Query(
        default=None,
        description="Filter by study format",
    ),
    study_pace_percentage: int | None = Query(
        default=None,
        description="Filter by study pace percentage",
    ),
    principal_type: PrincipalTypeEnum | None = Query(
        default=None,
        description="Filter by principal type",
    ),
):
    con = get_connection()
    query = """
    SELECT
        ep.education_provider,
        c.county,
        m.municipality,
        ep.principal_type,
        a.case_number,
        a.education_name,
        a.source_year,
        a.education_credits,
        a.decision,
        a.study_mode,
        a.study_pace_percentage,
        a.total_sought_places,
        a.total_granted_places,
        a.is_approved,
        a.is_distance,
        a.program_length_years
    FROM applications a
    LEFT JOIN education_provider ep
        ON a.education_provider_id = ep.id
    LEFT JOIN municipality m
        ON a.municipality_code = m.municipality_code
    LEFT JOIN county c
        ON m.county_code = c.county_code
    WHERE 1=1
        """
    params = []

    if year:
        query += " AND a.source_year = %s"
        params.append(year.value)
    if county:
        query += " AND c.county = %s"
        params.append(county.value)
    if is_approved is not None:
        query += " AND a.is_approved = %s"
        params.append(is_approved)
    if education_provider:
        query += " AND ep.education_provider ILIKE %s"
        params.append(f"%{education_provider}%")
    if municipality:
        query += " AND m.municipality ILIKE %s"
        params.append(f"%{municipality}%")
    if is_distance is not None:
        query += " AND a.is_distance = %s"
        params.append(is_distance)
    if study_pace_percentage is not None:
        query += " AND a.study_pace_percentage = %s"
        params.append(study_pace_percentage)
    if principal_type:
        query += " AND ep.principal_type = %s"
        params.append(principal_type.value)
    if format != FormatEnum.csv:
        query += " LIMIT %s"
        params.append(limit)

    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            applications = cursor.fetchall()

    if format == FormatEnum.csv:
        if not applications:
            return "No applications found"
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=applications[0].keys())
        writer.writeheader()
        writer.writerows(applications)
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=applications.csv"},
        )

    return applications


@app.get(
    "/statistics/education_area",
    summary="Get statistics for applications by county and education area",
    description="""
Shows number of applied spots, approved spots, and approval rate in percent per county and year.

**Allowed parameters:**

- `year` - Year of the applications

- `county` - Filter by county

- `education_area` - Filter by vocational area

""",
    response_description="Shows number of applied spots, approved spots, and approval rate in percent per county and year",
    response_model=list[StatisticsEducationArea],
)
async def get_county_statistics(
    format: FormatEnum = Query(
        default=FormatEnum.json,
        description="json or csv",
    ),
    year: YearEnum | None = Query(
        default=None,
        description="Year of the applications",
    ),
    county: CountyEnum | None = Query(
        default=None,
        description="Filter by county",
    ),
    education_area: EducationAreaEnum | None = Query(
        default=None,
        description="Filter by education area",
    ),
):
    con = get_connection()
    query = """
    SELECT
        a.source_year,
        c.county,
        ea.education_area,
        COUNT(*) AS application_count,
        SUM(a.total_sought_places) AS total_sought_places,
        SUM(a.total_granted_places) AS total_granted_places,
        ROUND(
        SUM(a.total_granted_places)::numeric
        / NULLIF(SUM(a.total_sought_places), 0) * 100,
        2
        ) AS approval_rate
    FROM applications a
    LEFT JOIN municipality m
        ON a.municipality_code = m.municipality_code
    LEFT JOIN county c
        ON m.county_code = c.county_code
    LEFT JOIN education_area ea
        ON a.education_area_id = ea.id
        WHERE 1 = 1
        """

    params = []

    if year:
        query += " AND a.source_year = %s"
        params.append(year.value)
    if county:
        query += " AND c.county = %s"
        params.append(county.value)
    if education_area:
        query += " AND ea.education_area = %s"
        params.append(education_area.value)

    query += """
    GROUP BY a.source_year, c.county, ea.education_area
    ORDER BY total_granted_places DESC
    """
    if format != FormatEnum.csv:
        query += " LIMIT 100"

    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            statistics = cursor.fetchall()

    if format == FormatEnum.csv:
        output = io.StringIO()

        if not statistics:
            return "No applications found"

        writer = csv.DictWriter(output, fieldnames=statistics[0].keys())
        writer.writeheader()
        writer.writerows(statistics)
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={
                "ConnectionAbortedError": "attachment; filename=education_area_statistics.csv"
            },
        )

    return statistics


@app.get(
    "/statistics/education_provider",
    summary="Get statistics per education provider",
    description="""
Returns statistics on applications grouped by education provider.
Shows which providers receive the most approved applications.

**Allowed parameters:**

- `year` — Filter statistics for a specific year

- `county` — Filter statistics for a specific county

    """,
    response_description="Statistics on applications grouped by education provider",
    response_model=list[StatisticsProvider],
)
async def get_statistics_education_provider(
    format: FormatEnum = Query(
        default=FormatEnum.json,
        description="json or csv",
    ),
    year: YearEnum | None = Query(
        default=None,
        description="Year of the applications",
    ),
    county: CountyEnum | None = Query(
        default=None,
        description="Filter by county",
    ),
    education_provider: str | None = Query(
        default=None,
        description="Filter by provider",
    ),
):
    """

    Endpoint for retrieving statistics per education provider.
    Shows who receives the most approved spots.

    """
    con = get_connection()
    query = """
    SELECT
        ep.education_provider,
        a.source_year,
        c.county,
        COUNT(*) AS application_count,
        SUM(a.total_sought_places) AS total_sought_places,
        SUM(a.total_granted_places) AS total_granted_places,
        ROUND(
            SUM(a.total_granted_places)::numeric
            / NULLIF(SUM(a.total_sought_places), 0) * 100,
            2
            ) AS approval_rate
    FROM applications a
    LEFT JOIN education_provider ep
        ON a.education_provider_id = ep.id
    LEFT JOIN municipality m
        ON a.municipality_code = m.municipality_code
    LEFT JOIN county c
        ON m.county_code = c.county_code
    WHERE 1 = 1
        """
    params = []

    if year:
        query += " AND a.source_year = %s"
        params.append(year.value)
    if county:
        query += " AND c.county = %s"
        params.append(county.value)
    if education_provider:
        query += " AND ep.education_provider ILIKE %s"
        params.append(f"%{education_provider}%")
    query += """
    GROUP BY ep.education_provider, a.source_year, c.county
    ORDER BY total_granted_places DESC
    """
    if format != FormatEnum.csv:
        query += " LIMIT 100"

    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            statistics = cursor.fetchall()

    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=statistics[0].keys())
        writer.writeheader()
        writer.writerows(statistics)
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=applications.csv"},
        )
    return statistics


@app.get(
    "/statistics/sun5",
    summary="Get statistics for applications with SUN 5 classification",
    description="""
Shows number of applied spots, approved spots, and approval rate in percent per county and year.

**Allowed parameters:**

- `year` - Year of the applications

- `lan` - Filter by county

- `kommun` - Filter by municipality


""",
    response_description="Shows number of applications, approved spots, and approval rate in percent per county, municipality, and year",
    response_model=list[StatisticsSun5],
)
async def get_statistics_sun5(
    year: YearEnumSun | None = Query(
        default=None,
        description="Year of the applications",
    ),
    lan: CountyEnum | None = Query(
        default=None,
        description="Filter by county",
    ),
    municipality: str | None = Query(
        default=None,
        description="Filter by municipality",
    ),
    sun5_name: str | None = Query(
        default=None,
        description="Filter by swedish educational nomenclature area",
    ),
):
    con = get_connection()
    query = """
    SELECT
        s.sun5_name,
        a.source_year,
        c.county,
        m.municipality,
        COUNT(*) AS application_count,
        COUNT(*) FILTER (
            WHERE a.is_approved = TRUE
        ) AS approved_application_count,
        ROUND(
            COUNT(*) FILTER (
                WHERE a.is_approved = TRUE
            )::numeric
            / NULLIF(COUNT(*), 0) * 100,
            2
        ) AS application_approval_rate,
        SUM(a.total_sought_places) AS total_sought_places,
        SUM(a.total_granted_places) AS total_granted_places,
        ROUND(
            SUM(a.total_granted_places)::numeric
            / NULLIF(SUM(a.total_sought_places), 0) * 100,
            2
        ) AS place_approval_rate
    FROM applications a
    LEFT JOIN sun5 s
        ON a.sun5_code = s.sun5_code
    LEFT JOIN municipality m
        ON a.municipality_code = m.municipality_code
    LEFT JOIN county c
        ON m.county_code = c.county_code
    WHERE a.source_year >= 2023
    """
    params = []

    if year:
        query += " AND a.source_year = %s"
        params.append(year.value)
    if lan:
        query += " AND c.county = %s"
        params.append(lan.value)
    if municipality:
        query += " AND m.municipality ILIKE %s"
        params.append(f"%{municipality}%")
    if sun5_name:
        query += " AND s.sun5_name ILIKE %s"
        params.append(f"%{sun5_name}%")
    query += """
GROUP BY
    s.sun5_name,
    a.source_year,
    c.county,
    m.municipality
ORDER BY total_granted_places DESC
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            statistics = cursor.fetchall()

    return statistics


@app.get(
    "/statistics/education_capacity",
    summary="Get statistics for education capacity",
    description="Population and granted places in Sweden, MYH, 2020-2025",
)
async def get_statistics_education_capacity(
    year: YearEnum | None = None,
):

    con = get_connection()

    query = """
    SELECT
        c.county,
        a.source_year,
        MAX(p.population) AS population,
        COUNT(*) AS application_count,
        COUNT(*) FILTER (
            WHERE a.is_approved = TRUE
        ) AS approved_application_count,
        ROUND(
            COUNT(*) FILTER (WHERE a.is_approved = TRUE)::numeric / 
            NULLIF(COUNT(*), 0) * 100, 2) AS application_approval_rate,
        SUM(a.total_sought_places) AS total_sought_places,
        SUM(a.total_granted_places) AS granted_places,
        ROUND(SUM(a.total_granted_places)::numeric / 
            NULLIF(MAX(p.population), 0) * 1000, 2) AS granted_places_per_1000,
        SUM(a.total_sought_places) AS total_sought_places,
        ROUND(SUM(a.total_granted_places)::numeric / 
        NULLIF(SUM(a.total_sought_places), 0) * 100, 2) AS place_approval_rate
    FROM municipality m
    JOIN population p
        ON m.municipality_code = p.municipality_code
    JOIN county c
        ON m.county_code = c.county_code
    JOIN applications a
        ON m.municipality_code = a.municipality_code
        AND p.year = a.source_year
    WHERE 1 = 1
"""
    params = []

    if year:
        query += " AND a.source_year = %s"
        params.append(year.value)
    query += """
    GROUP BY c.county, a.source_year
    ORDER BY granted_places DESC
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()
    return data


@app.get(
    "/statistics/top_education_area",
    summary="Get statistics for education area",
)
async def get_statistics_top_education_area(
    year: YearEnum | None = None,
):
    con = get_connection()

    query = """ 
        SELECT
            ea.education_area,
            SUM(a.total_granted_places) AS granted_places
        FROM applications a
        JOIN education_area ea
            ON ea.id = a.education_area_id
        WHERE 1 = 1
    """

    params = []

    if year:
        query += " AND a.source_year = %s"
        params.append(year.value)
    query += """
    GROUP BY ea.education_area
    ORDER BY granted_places DESC
    LIMIT 5
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            statistics = cursor.fetchall()
    return statistics


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
