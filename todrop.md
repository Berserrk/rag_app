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
