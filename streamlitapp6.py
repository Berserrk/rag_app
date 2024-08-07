import streamlit as st
import json
from pathlib import Path

# ... (previous code remains the same) ...

# After the Entity Summaries section, add the following:

st.subheader("📊 Categorization:")

# Load the categorization data from a JSON file
CATEGORIZATION_FILE = Path("outputs") / "categorization.json"
with open(CATEGORIZATION_FILE, "r") as f:
    categorization_data = json.load(f)

# Create a dropdown list using the keys from the JSON file
selected_category = st.selectbox("**Select a category**", list(categorization_data.keys()))

# Display the information for the selected category
if selected_category in categorization_data:
    st.info(categorization_data[selected_category])
else:
    st.warning("No information available for the selected category.")

# ... (rest of the previous code remains the same) ...