# Sample data
data = {'Name': ['John', 'Jane', 'Bob', 'Alice'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'London', 'Paris', 'Tokyo']}

df = pd.DataFrame(data)

# Display the table with rotated column names
st.title("My Table")
col_names = df.columns
col_widths = [200, 200, 400]  # Adjust the column widths in pixels

with st.expander("Table"):
    # Create a container to hold the table
    with st.container():
        # Create a row for the column names
        row = st.columns(len(col_names), gap="medium")
        for i, name in enumerate(col_names):
            with row[i]:
                # Use Markdown to create a rotated column name
                st.markdown(f"<div style='transform: rotate(-45deg); text-align: right;'>{name}</div>", unsafe_allow_html=True)
                # Set the column width programmatically
                st.write(f'<div style="width:{col_widths[i]}px;">&nbsp;</div>', unsafe_allow_html=True)

        # Display the table data
        st.dataframe(df)
