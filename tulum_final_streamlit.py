import streamlit as st
from debug_backend import main
import time
import pandas as pd

# Get vibe from user
vibe = st.sidebar.text_input("Vibe")

# Add input here on price
# Add input here on number of rooms

# Create a button in the sidebar
submit_button = st.sidebar.button("Submit")

# Add a selectbox in the sidebar for sorting options
sort_option = st.sidebar.selectbox(
    "Sort by",
    ('None', 'Hotel', 'Score', 'Website', 'Rooms', 'Per room cost')
)

# Only run the functions when the button is clicked
if submit_button:
    start_time = time.time()
    ranked_scores, websites = main(vibe)
    print("Time taken by main: ", time.time() - start_time)

    start_time = time.time()
    df = pd.DataFrame(ranked_scores, columns=['Hotel', 'Score', 'Website', 'Rooms', 'Per room cost'])

    # Sort the DataFrame if a sort option is selected
    if sort_option != 'None':
        df = df.sort_values(by=sort_option)

    st.dataframe(df)
    print("Time taken by Streamlit: ", time.time() - start_time)