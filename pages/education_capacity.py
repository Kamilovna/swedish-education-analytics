import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import plotly.express as px
from schemas import YearEnum
import json

API_URL = "http://localhost:8000"

YEAR = [year.value for year in YearEnum]


def education_capacity_page():

    def red_bar():
        st.markdown(
            """
            <div style="
                width:50px;
                height:6px;
                background:#E3120B;
                margin_bottom:15px;">
            </div>
            """,
            unsafe_allow_html=True,
        )

    year = st.sidebar.selectbox(
        "Choose a year",
        YEAR,
        index=len(YEAR) - 1,
        key="capacity_year",
    )
    st.title("Education capacity")

    st.subheader(f"Vacational education overview (MYH), {year}")
    k1, k2, k3, k4, k5 = st.columns(5)

    resp = requests.get(
        f"{API_URL}/statistics/education_capacity", params={"year": year}
    )

    resp.raise_for_status()
    df = pd.DataFrame(resp.json())

    total_population = df["population"].sum()
    total_applications = df["application_count"].sum()
    approved_application_count = df["approved_application_count"].sum()
    application_approval_rate = round(
        approved_application_count / total_applications * 100, 2
    )
    total_granted = df["granted_places"].sum()
    total_sought_places = df["total_sought_places"].sum()
    place_approval_rate = round(total_granted / total_sought_places * 100, 2)

    with k1:
        st.metric("Population", f"{total_population / 1_000_000:.1f} M")
    with k2:
        st.metric("Sought places", f"{total_sought_places:,.0f}")
    with k3:
        st.metric("Number of applications", f"{total_applications:,.0f}")
    with k4:
        st.metric("Granted places", f"{total_granted:,.0f}")
    with k5:
        st.metric("Granted places rate", f"{place_approval_rate:,.1f}")

    g1, g2 = st.columns(2)
    with g1:
        red_bar()

        fig = px.scatter(
            df,
            x="population",
            y="granted_places_per_1000",
            size="application_count",
            hover_name="county",
            labels={
                "population": "Population",
                "granted_places": "Granted places",
                "application_count": "Number of applications",
                "granted_places_per_1000": "Places per 1,000",
            },
        )

        st.subheader("Population and granted places by county")
        st.markdown(
            """
            Bubble size indicates the **population**, while the y-axis shows
            granted places per **1,000 inhabitants**.
            """
        )

        fig.update_traces(
            marker=dict(color="#E3120B", opacity=0.75, line=dict(width=0))
        )

        fig.update_layout(
            template="simple_white",
            height=450,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="#F7F3EE",
            paper_bgcolor="white",
            hoverlabel=dict(bgcolor="#F7F3EE", font_size=12, font_color="#333333"),
        )

        fig.update_xaxes(
            title="Population", showgrid=True, gridcolor="#e6e6e6", zeroline=False
        )

        fig.update_yaxes(
            title=None,
            showgrid=True,
            gridcolor="#e6e6e6",
            zeroline=True,
        )

        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br><br>"
            + "Population:           %{x:,.0f}<br>"
            + "Places per 1,000:       %{y:.2f}<br>"
            + "<extra></extra>"
        )

        top = df.nlargest(5, "population")
        for _, row in top.iterrows():
            fig.add_annotation(
                x=row["population"],
                y=row["granted_places_per_1000"],
                text=row["county"],
                showarrow=False,
                xshift=15,
                yshift=18,
                font=dict(size=12, color="#333333"),
            )

        st.plotly_chart(fig)

        with open("data/sweden_counties.json", encoding="utf-8") as f:
            geojson = json.load(f)

    with g2:
        red_bar()

        st.subheader("Granted study places per 1,000 inhabitats by county")
        st.markdown(
            "<span style='color:#E3120B;'>■</span> Darker red indicates higher education capacity",
            unsafe_allow_html=True,
        )

        geo_counties = [f["properties"]["name"] for f in geojson["features"]]

        fig_map = px.choropleth(
            df,
            geojson=geojson,
            locations="county",
            featureidkey="properties.name",
            color="granted_places_per_1000",
            color_continuous_scale=["#FCE8E6", "#F4B7B2", "#E57368", "#e3120B"],
        )

        fig_map.update_geos(
            fitbounds="locations", bgcolor="#F7F3EE", visible=False, projection_scale=8
        )

        fig_map.update_layout(
            coloraxis_showscale=False,
            paper_bgcolor="#F7F3EE",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            hoverlabel=dict(bgcolor="#F7F3EE", font_size=12, font_color="#333333"),
        )

        fig_map.update_traces(
            hovertemplate="<b>%{location}</b><br> %{z:.2f}<extra></extra>",
            marker_line_color="white",
            marker_line_width=1,
        )

        labels = pd.DataFrame(
            {
                "county": ["Stockholm", "Skåne", "Västra Götaland"],
                "lat": [59.3, 55.6, 57.7],
                "lon": [18.1, 13.0, 12.0],
            }
        )
        fig_map.add_scattergeo(
            lat=labels["lat"],
            lon=labels["lon"],
            text=labels["county"],
            mode="text",
            textfont=dict(size=12, color="#333333"),
            hoverinfo="skip",
            hovertemplate=None,
            showlegend=False,
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with g1:
        red_bar()

        st.subheader("Top 5 educational area by granted places")
        st.caption("Source: Myndigheten för yrkeshögskolan (MYH)")

        resp = requests.get(
            f"{API_URL}/statistics/top_education_area", params={"year": year}
        )

        resp.raise_for_status()
        df = pd.DataFrame(resp.json())

        fig = px.bar(
            df.sort_values("granted_places"),
            x="granted_places",
            y="education_area",
            orientation="h",
        )

        fig.update_traces(marker_color="#e3120B", hovertemplate="%{x:,}<extra></extra>")

        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            paper_bgcolor="#F7F3EE",
            plot_bgcolor="#F7F3EE",
            height=250,
            bargap=0.4,
        )

        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False)

        st.plotly_chart(fig)
