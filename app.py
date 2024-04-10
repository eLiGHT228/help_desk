import streamlit as st
from config.config import stconfig

if __name__ == "__main__":
    stconfig()
    st.switch_page("pages/login.py")

