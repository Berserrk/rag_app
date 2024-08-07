import streamlit as st
import json
from pathlib import Path

# ... (previous code remains the same until the Entity Summaries section) ...

st.subheader("🌍 Entity Summaries:")

st.write("Flagged Entities Description and Categorization")

# Load the original capitals data
with open(PATH_TO_ENTITIES, "r") as f:
    capitals = json.load(f)

# Load the categorization data
CATEGORIZATION_FILE = Path("outputs") / "categorization.json"
with open(CATEGORIZATION_FILE, "r") as f:
    categorization_data = json.load(f)

# Get the list of countries (entities)
countries = list(country_status.keys())

# Create the dropdown for entity selection
selected_country = st.selectbox("**Select an entity**", countries)

if selected_country in capitals:
    # Display the original summary
    st.info("Entity Summary:")
    st.write(capitals[selected_country])
    
    # Display the categorization information
    if selected_country in categorization_data:
        st.success("Entity Categorization:")
        st.write(categorization_data[selected_country])
    else:
        st.warning("No categorization information available for this entity.")
else:
    st.error("No information available for the selected entity.")

# ... (rest of the previous code remains the same) ...