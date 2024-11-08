import streamlit as st
import pandas as pd

# Sample data
data = {
    "Frozen Column": ["Row 1", "Row 2", "Row 3", "Row 4"],
    "Column 1": [10, 20, 30, 40],
    "Column 2": [15, 25, 35, 45],
    "Column 3": [20, 30, 40, 50],
}

df = pd.DataFrame(data)

# Inject custom CSS to style the scrollbar
st.markdown("""
    <style>
    /* Width of the scrollbar */
    ::-webkit-scrollbar {
        width: 16px;  /* Make the scrollbar wider */
        height: 16px; /* For horizontal scrollbar */
    }

    /* Background of the scrollbar */
    ::-webkit-scrollbar-track {
        background: #f1f1f1;  /* Light background color for scrollbar track */
    }

    /* Handle color of the scrollbar */
    ::-webkit-scrollbar-thumb {
        background: #888;  /* Darker color for scrollbar thumb */
        border-radius: 10px; /* Rounded corners for thumb */
    }

    /* Handle hover color of the scrollbar */
    ::-webkit-scrollbar-thumb:hover {
        background: #555;  /* Darker color on hover */
    }

    /* Firefox scrollbar styling */
    body {
        scrollbar-width: auto;
        scrollbar-color: #888 #f1f1f1;
    }
    </style>
""", unsafe_allow_html=True)

# Set up Streamlit layout with two columns
col1, col2 = st.columns([1, 5])

# Display the frozen column in the left section
with col1:
    st.write("Frozen Column")
    st.data_editor(df[["Frozen Column"]], hide_index=True)

# Display the scrollable columns in the right section
with col2:
    st.write("Scrollable Columns")
    st.data_editor(df.drop(columns=["Frozen Column"]), hide_index=True)
