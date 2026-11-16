"""OralScreen AI: project website (home page) and screening app in one Streamlit deployment."""
import streamlit as st

pages = [
    st.Page("website/site.py", title="OralScreen AI | Project", default=True),
    st.Page("screening.py", title="OralScreen AI | Screening app", url_path="screening"),
]
st.navigation(pages, position="hidden").run()
