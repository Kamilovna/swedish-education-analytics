import streamlit as st
from pages.applications import applications_page
from pages.education_capacity import education_capacity_page

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Swedish Education Analytics", layout="wide")

pg = st.navigation(
    [
        st.Page(applications_page, title="Applications"),
        st.Page(education_capacity_page, title="Education capacity"),
    ]
)

pg.run()
