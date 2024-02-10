import streamlit as st
from tulum_final import main
import time
import pandas as pd

st.sidebar.write("You must input a vibe and push submit for the results to appear.")

# Get vibe from user
vibe = st.sidebar.text_input("Vibe")

# Add a selectbox in the sidebar for CSV file selection
csv_file = st.sidebar.selectbox(
    'Select CSV file',
    ('./enriched_price_tulum_hotels.csv', './jn_improved_data.csv')  # replace with your actual file paths
)

# Add input here on price
# Add input here on number of rooms

# Create a button in the sidebar
submit_button = st.sidebar.button("Submit")

# Add a selectbox in the sidebar for sorting options
sort_option = st.sidebar.selectbox(
    "Sort by",
    ('None', 'Name', 'Score', 'Website', 'City', 'Rating', 'Description', 'Email', 'Website Description', 'Subtypes')
)

# Add a selectbox in the sidebar for sort order
sort_order = st.sidebar.selectbox(
    "Sort order",
    ('Descending', 'Ascending')
)

# Only run the functions when the button is clicked
if submit_button:
    ranked_scores, websites = main(vibe, csv_file)

    df = pd.DataFrame(ranked_scores, columns=['Name', 'Score', 'Website', 'City', 'Rating', 'Description', 'Email', 'Website Description', 'Subtypes', 'Photo'])

    # Convert the 'Website' and 'Photo' columns to HTML links and image tags
    df['Website'] = df['Website'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
    df['Photo'] = df['Photo'].apply(lambda x: f'<img src="{x}" width="175" >')  # Increase the width to 250 pixels

    # Rearrange the columns to display them in the specified order
    df = df[['Name', 'Score', 'Subtypes', 'Rating', 'City', 'Photo', 'Description', 'Website Description', 'Website', 'Email']]

    # Sort the DataFrame if a sort option is selected
    if sort_option != 'None':
        df = df.sort_values(by=[sort_option, 'Score'], ascending=[(sort_order == 'Descending'), False])
        
        # Reset the index of the DataFrame to maintain the integrity of the "score" ranking
        df.reset_index(drop=True, inplace=True)

        # Convert the DataFrame to HTML and display it using st.markdown
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)