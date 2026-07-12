from pydantic import BaseModel
from enum import Enum


class YearEnum(int, Enum):
    y2020 = 2020
    y2021 = 2021
    y2022 = 2022
    y2023 = 2023
    y2024 = 2024
    y2025 = 2025


class YearEnumSun(int, Enum):
    y2023 = 2023
    y2024 = 2024
    y2025 = 2025


class FormatEnum(str, Enum):
    json = "json"
    csv = "csv"


class StudyPace(int, Enum):
    FIFTY = 50
    SEVENTY_FIVE = 75
    ONE_HUNDRED = 100


class CountyEnum(str, Enum):
    STOCKHOLM = "Stockholm"
    UPPSALA = "Uppsala"
    SODERMANLAND = "Södermanland"
    OSTERGOTLAND = "Östergötland"
    JONKOPING = "Jönköping"
    KRONOBERG = "Kronoberg"
    KALMAR = "Kalmar"
    GOTLAND = "Gotland"
    BLEKINGE = "Blekinge"
    SKANE = "Skåne"
    HALLAND = "Halland"
    VASTRA_GOTALAND = "Västra Götaland"
    VARMLAND = "Värmland"
    OREBRO = "Örebro"
    VASTMANLAND = "Västmanland"
    DALARNA = "Dalarna"
    GAVLEBORG = "Gävleborg"
    VASTERNORRLAND = "Västernorrland"
    JAMTLAND = "Jämtland"
    VASTERBOTTEN = "Västerbotten"
    NORRBOTTEN = "Norrbotten"


class EducationAreaEnum(str, Enum):
    DATA_IT = "Data/It"
    ECONOMICS_ADMINISTRATION_AND_SALES = "Ekonomi, Administration Och Försäljning"
    WELLNESS_AND_BODY_CARE = "Friskvård Och Kroppsvård"
    HEALTHCARE_AND_SOCIAL_WORK = "Hälso- Och Sjukvård Samt Socialt Arbete"
    HOTEL_RESTAURANT_AND_TOURISM = "Hotell, Restaurang Och Turism"
    JOURNALISM_AND_INFORMATION = "Journalistik Och Information"
    LAW = "Juridik"
    CULTURE_MEDIA_AND_DESIGN = "Kultur, Media Och Design"
    AGRICULTURE_ANIMAL_CARE_GARDENING_FORESTRY_AND_FISHING = (
        "Lantbruk, Djurvård, Trädgård, Skog Och Fiske"
    )
    OTHER = "Övrigt"
    PEDAGOGY_AND_EDUCATION = "Pedagogik Och Undervisning"
    SECURITY_SERVICES = "Säkerhetstjänster"
    COMMUNITY_DEVELOPMENT_AND_CONSTRUCTION = "Samhällsbyggnad Och Byggteknik"
    TECHNOLOGY_AND_MANUFACTURING = "Teknik Och Tillverkning"
    TRANSPORT_SERVICES = "Transporttjänster"


class Application(BaseModel):
    education_provider: str
    county: str
    municipality: str
    principal_type: str
    case_number: str
    education_name: str
    source_year: int
    education_credits: int
    decision: str
    study_mode: str
    study_pace_percentage: int
    total_sought_places: int
    total_granted_places: int
    is_approved: bool
    is_distance: bool
    program_length_years: float


class ApplicationsResponse(BaseModel):
    total: int
    items: list[Application]


class StatisticsEducationArea(BaseModel):
    source_year: int
    county: str
    education_area: str
    application_count: int
    total_sought_places: int
    total_granted_places: int
    approval_rate: float


class StatisticsProvider(BaseModel):
    education_provider: str
    source_year: int
    county: str
    application_count: int
    total_sought_places: int
    total_granted_places: int
    approval_rate: float


class StatisticsCounty(BaseModel):
    source_year: int
    county: str
    antal_beviljade: int
    approval_rate: float


class PrincipalTypeEnum(str, Enum):
    statlig = "Statlig"
    kommun = "Kommun"
    Region = "Region"
    privat = "Privat"


class StatisticsSun5(BaseModel):
    sun5_name: str | None
    source_year: int
    county: str | None
    municipality: str | None
    application_count: int
    approved_application_count: int
    application_approval_rate: float | None
    total_sought_places: int
    total_granted_places: int
    place_approval_rate: float | None
