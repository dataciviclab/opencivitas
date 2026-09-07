#!/usr/bin/env python3
"""
OpenCivitas Intelligence · Dashboard Streamlit
Profilo dei comuni italiani: finanza (FSC) × servizi (indicatori)
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="OpenCivitas Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="opencivitas",
    repo_url="https://github.com/dataciviclab/opencivitas",
)

pages = {
    "": [
        st.Page("pages/01_mappa.py", title="Mappa Italia", icon="🗺️", default=True),
        st.Page("pages/02_profilo.py", title="Profilo Comune", icon="🏛️"),
    ],
    "Analisi": [
        st.Page("pages/03_classifiche.py", title="Classifiche", icon="🏆"),
        st.Page("pages/04_trend.py", title="Trend", icon="📈"),
        st.Page("pages/06_indicatori.py", title="Indicatori", icon="📊"),
    ],
    "Strumenti": [
        st.Page("pages/05_esplora.py", title="SQL Explorer", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

pg.run()
