# Healthcare_Dashboard
In modern healthcare, data is critical for improving patient care and operational efficiency. However, analyzing large volumes of patient and treatment data remains challenging. This project aims to build an interactive analytics dashboard

# ------------------------ Import Libraries ----------------------------- #
import pandas as pd
import streamlit as st
import plotly.express as px
import json
import requests


st.write("My first Streamlit Dashboard 🎈")


@st.cache_data

def load_data():
  return pd.read_csv("https://github.com/dataprofessor/population-dashboard/raw/master/data/us-population-2010-2019-reshaped.csv", index_col=0