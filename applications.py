import streamlit as st
import requests
import pandas as pd
from schemas import YearEnum, CountyEnum, EducationAreaEnum
import plotly.express as px
from urllib.parse import urlencode

API_URL = "http://localhost:8000"

YEARS = [""] + [str(year.value) for year in YearEnum]

COUNTY = [""] + [str(county_name.value) for county_name in CountyEnum]

EDUCATIONAREA = [""] + [str(area_name.value) for area_name in EducationAreaEnum]

st.set_page_config(page_title="Applications YH", layout="wide")
st.title("Applications to education")

st.subheader("Search applications")

col1, col2, col3 = st.columns(3)
with col1:
    year = st.selectbox("Year", YEARS, key="app_year")
    county = st.selectbox("County", COUNTY, key="app_county")
    is_distance = st.selectbox("Study form", ["All", "Online", "On-campus"])
with col2:
    education_provider = st.text_input(
        "Provider (free text)", key="app_education_provider"
    )
    municipality = st.text_input("Municipality (free text)", key="app_municipality")
    principal_type = st.selectbox(
        "Principal type",
        ["All", "State", "Municipality", "Region", "Private"],
        key="app_principal_type",
    )
with col3:
    study_pace_percentage = st.selectbox(
        "Study pace %", [None, 50, 75, 100], key="app_study_pace_percentage"
    )
    is_approved = st.selectbox("Approved", ["All", "Yes", "No"], key="app_approved")
    limit = st.slider(
        "Max number of results",
        min_value=1,
        max_value=100,
        value=20,
        key="app_limit",
    )

if st.button("Get applications", key="btn_app"):
    params = {"limit": limit}
    if year:
        params["year"] = year
    if county:
        params["county"] = county
    if is_distance == "Online":
        params["is_distance"] = True
    elif is_distance == "On-campus":
        params["is_distance"] = False
    if education_provider:
        params["education_provider"] = education_provider
    if municipality:
        params["municipality"] = municipality
    if is_approved == "Yes":
        params["is_approved"] = "true"
    elif is_approved == "No":
        params["is_approved"] = "false"
    if principal_type == "State":
        params["principal_type"] = "Statlig"
    elif principal_type == "Municipality":
        params["principal_type"] = "Kommun"
    elif principal_type == "Region":
        params["principal_type"] = "Region"
    elif principal_type == "Private":
        params["principal_type"] = "Privat"
    if study_pace_percentage is not None:
        params["study_pace_percentage"] = study_pace_percentage

    try:
        resp = requests.get(f"{API_URL}/applications", params=params)
        resp.raise_for_status()
        data = resp.json()
        if data["items"]:
            st.success(f"{data['total']} applications found")
            st.dataframe(pd.DataFrame(data["items"]), use_container_width=True)

            export_params = {
                key: value for key, value in params.items() if key != "limit"
            }
            export_params["format"] = "csv"
            export_url = f"{API_URL}/applications?{urlencode(export_params)}"
            st.markdown(f"[Download as CSV]({export_url})")
        else:
            st.info("No applications found for the selected filters.")
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the API. Make sure the server is running on port 8000."
        )
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e}")
