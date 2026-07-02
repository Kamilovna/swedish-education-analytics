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

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Applications",
        "Statistics by field of education",
        "Statistics by provider",
        "Sun 5 - statistics, 2023 - 2025",
    ]
)

with tab1:
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
        limit = st.slider(
            "Max number of results",
            min_value=1,
            max_value=100,
            value=20,
            key="app_limit",
        )
        study_pace_percentage: int = st.select_slider(
            "Study pace %", options=[50, 75, 100], key="app_study_pace_percentage"
        )
        is_approved = st.selectbox("Approved", ["All", "Yes", "No"], key="app_approved")

    if st.button("Get applications", key="btn_app"):
        params = {"limit": limit}
        if year:
            params["year"] = year
        if county:
            params["county"] = county
        if is_distance == "Online":
            params["is_distance"] = "True"
        elif is_distance == "On-campus":
            params["is_distance"] = "False"
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
        if study_pace_percentage:
            params["study_pace_percentage"] = study_pace_percentage

        try:
            resp = requests.get(f"{API_URL}/applications", params=params)
            resp.raise_for_status()
            data = resp.json()
            if data:
                st.success(f"{len(data)} applications found")
                st.dataframe(pd.DataFrame(data), use_container_width=True)

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


with tab2:
    st.subheader("Statistics by field of education")

    col1, col2, col3 = st.columns(3)
    with col1:
        year2 = st.selectbox("Year", YEARS, key="stat_year")
    with col2:
        county2 = st.selectbox("County", COUNTY, key="stat_lan")
    with col3:
        area = st.selectbox("Field of education", EDUCATIONAREA, key="stat_omrade")

    if st.button("Fetch statistics", key="btn_stat"):
        params = {}
        if year2:
            params["year"] = year2
        if county2:
            params["county"] = county2
        if area:
            params["education_area"] = area

        try:
            resp = requests.get(f"{API_URL}/statistics/education_area", params=params)
            resp.raise_for_status()
            data = resp.json()
            if data:
                df = pd.DataFrame(data)
                st.success(f"{len(df)} rows")
                st.dataframe(df, use_container_width=True)

                if (
                    "education_area" in df.columns
                    and "total_granted_places" in df.columns
                ):
                    chart_data = (
                        df.groupby("education_area")["total_granted_places"]
                        .sum()
                        .sort_values(ascending=False)
                        .reset_index()
                    )
                    if len(chart_data) > 1:
                        fig = px.bar(
                            chart_data,
                            x="education_area",
                            y="total_granted_places",
                            category_orders={
                                "education_area": chart_data["education_area"].tolist()
                            },
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    export_params = {key: value for key, value in params.items()}
                    export_params["format"] = "csv"
                    export_url = f"{API_URL}/statistics/education_area?{urlencode(export_params)}"
                    st.markdown(f"[Download as CSV]({export_url})")
            else:
                st.info("No statistics found for the selected filters.")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the API. Make sure the server is running on port 8000."
            )
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e}")


with tab3:
    st.subheader("Statistics by education provider")

    col1, col2, col3 = st.columns(3)
    with col1:
        year3 = st.selectbox("Year", YEARS, key="anord_year")
    with col2:
        county3 = st.selectbox("County", COUNTY, key="anord_lan")
    with col3:
        education_provider3 = st.text_input("Provider (free text)", key="anord_name")

    if st.button("Fetch statistics", key="btn_anord"):
        params = {}
        if year3:
            params["year"] = year3
        if county3:
            params["lan"] = county3
        if education_provider3:
            params["anordnare"] = education_provider3

        try:
            resp = requests.get(
                f"{API_URL}/statistics/education_provider", params=params
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                df = pd.DataFrame(data)
                st.success(f"{len(df)} providers")
                st.dataframe(df, use_container_width=True)

                if len(df) > 0 and "total_granted_places" in df.columns:
                    top10 = (
                        df.groupby("education_provider")["total_granted_places"]
                        .sum()
                        .nlargest(10)
                        .reset_index()
                    )
                    st.subheader("Top 10 providers (approved places)")
                    fig = px.bar(
                        top10,
                        x="total_granted_places",
                        y="education_provider",
                        orientation="h",
                        category_orders={
                            "education_provider": top10["education_provider"].tolist()
                        },
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No statistics found for the selected filters.")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the API. Make sure the server is running on port 8000."
            )
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e}")

with tab4:
    sidebar_col, main_col = st.columns([1, 3])

    with sidebar_col:
        st.subheader("Filter")
        year4 = st.selectbox("Year", ["All", "2023", "2024", "2025"], key="dash_year")
        county4 = st.selectbox("County", COUNTY, key="dash_lan")
        municipality4 = st.text_input("Municipality (free text)", key="dash_county")
        sun5 = st.text_input("SUN5 nomenclature (free text)", key="dash_sun5")

    with main_col:
        st.subheader("Dashboard — Statistics 2023–2025")

        params4 = {}
        if year4 != "All":
            params4["year"] = year4
        if county4:
            params4["county"] = county4
        if municipality4:
            params4["municipality"] = municipality4
        if sun5:
            params4["sun5_name"] = sun5

        try:
            resp4 = requests.get(f"{API_URL}/statistics/sun5", params=params4)
            resp4.raise_for_status()
            data4 = resp4.json()

            if municipality4:
                app_params = {"year": year4, "limit": 100}
                if county4:
                    app_params["county"] = county4
                app_params["municipality"] = municipality4
                resp_app = requests.get(f"{API_URL}/statistics/sun5", params=app_params)
                resp_app.raise_for_status()
                app_data = resp_app.json()
            else:
                app_data = None

            if data4:
                df4 = pd.DataFrame(data4)

                m1, m2, m3, m4, m5, m6 = st.columns(6)
                application_count = df4["application_count"].sum()
                approved_application_count = df4["approved_application_count"].sum()
                application_approval_rate = (
                    round(approved_application_count / application_count * 100, 2)
                    if application_count
                    else 0
                )
                total_sought_places = df4["total_sought_places"].sum()
                total_granted_places = df4["total_granted_places"].sum()
                place_approval_rate = (
                    round(total_granted_places / total_sought_places * 100, 2)
                    if total_sought_places
                    else 0
                )

                m1.metric("Total applications", int(application_count))
                m2.metric("Approved applications", int(approved_application_count))
                m3.metric("Approval rate", f"{application_approval_rate}%")
                m4.metric("Applied places", int(total_sought_places))
                m5.metric("Approved places", int(total_granted_places))
                m6.metric("Approval rate", f"{place_approval_rate}%")

                chart_data4 = (
                    df4.groupby("sun5_name")[
                        ["total_granted_places", "total_sought_places"]
                    ]
                    .sum()
                    .reset_index()
                    .nlargest(10, "total_granted_places")
                    .sort_values("total_granted_places", ascending=True)
                )
                chart_melt4 = chart_data4.melt(
                    id_vars="sun5_name",
                    value_vars=["total_sought_places", "total_granted_places"],
                    var_name="type",
                    value_name="count",
                )
                chart_melt4["type"] = chart_melt4["type"].replace(
                    {
                        "total_sought_places": "Applied places",
                        "total_granted_places": "Approved places",
                    }
                )
                fig4 = px.bar(
                    chart_melt4,
                    x="count",
                    y="sun5_name",
                    color="type",
                    orientation="h",
                    barmode="overlay",
                    height=500,
                    title="TOP 10 - Approved places by SUN5 nomenclature",
                    labels={"sun5_name": "", "count": "", "type": ""},
                )
                fig4.update_traces(
                    hovertemplate="%{fullData.name}<br><span style='font-size:16px'><b>%{x}</b></span><extra></extra>"
                )
                fig4.update_layout(xaxis_title="")

                st.plotly_chart(fig4, use_container_width=True)

                st.dataframe(df4, use_container_width=True)

                if app_data:
                    st.subheader(f"Applications in municipality: {municipality4}")
                    st.dataframe(pd.DataFrame(app_data), use_container_width=True)
            else:
                st.info("No statistics found for the selected filters.")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the API. Make sure the server is running on port 8000."
            )
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e}")
