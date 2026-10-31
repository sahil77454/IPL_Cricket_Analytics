
import streamlit as st


def apply_custom_styles():

    st.markdown("""
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* Main headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #121a27;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #192333;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #29364a;
    }

    [data-testid="stMetricLabel"] {
        color: #aebbd0;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-weight: bold;
    }

    /* Buttons */
    .stButton button {
        background-color: #e63946;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #b92735;
        color: white;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: white;
    }

    /* Dividers */
    hr {
        border-color: #29364a;
    }

    </style>
    """, unsafe_allow_html=True)
