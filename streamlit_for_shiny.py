import streamlit as st
from backend import main
import pandas as pd
from backend import query_and_append
from backend import fetch_and_prepare_data

# Get query from user
query = st.sidebar.text_input("Input Query")

# Give user example of how to input query
st.sidebar.write("""
Query must look like: Boutique Hotels, Lake Garda, Italy.         
""")

# MUST get country code for outscraper to work. 
country_code = st.sidebar.text_input("Country Code (e.g. US, UK, IT)")

# Get vibe from user
vibe = st.sidebar.text_input("Vibe")

# Give user example of how to input vibe
st.sidebar.write("Vibe: e.g. We are looking for something minimalist, with open ocean views, natural wooden elements, and old-world charm. We want more of a campus-like set up, where our party can explore the larger grounds.")

# Create a button in the sidebar
submit_button = st.sidebar.button("Submit")

# Only run the functions when the button is clicked
if submit_button:
    # Call the outscraper api and store the results in this variable
    outscraper_results = query_and_append(query=query, country_code=country_code)

    fetch_and_prepare_data()

    # Call the function with a user input
    hotel_output = main(query, country_code, vibe)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(hotel_output)

    # Convert the 'website' and 'email' columns to clickable links
    df['website'] = df['website'].apply(lambda x: f'<a href="{x}">{x}</a>' if x else "")
    df['email'] = df['email'].apply(lambda x: f'<a href="mailto:{x}">{x}</a>' if x else "")

    # Display the DataFrame as a table in Streamlit
    st.write(df.to_html(escape=False), unsafe_allow_html=True)