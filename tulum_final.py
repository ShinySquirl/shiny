import pandas as pd
import numpy as np
import pickle
import os
import openai
from dotenv import load_dotenv

# Load .env file from the specific path
load_dotenv('.env')


openai.api_key = os.getenv('OPENAI_API_KEY')   
model_id = 'text-embedding-3-small'  # or 'text-embedding-3-large'


def create_embeddings(data):
    embeddings = {}
    websites = {}
    client = openai.OpenAI()  # Create an OpenAI client instance
    for row in data:
        if 'site' in row:  # Check if 'site' is in the row
            websites[row['name']] = row['site']  # Map hotel name to website
        else:
            websites[row['name']] = None  # Use None or a default value if 'site' is not in the row
        input_text = ' '.join(str(value) for value in row.values())  # Convert the entire row to a single string
        response = client.embeddings.create(input=[input_text], model=model_id)  # Use the correct method
        embeddings[row['name']] = response.data[0].embedding
    return embeddings, websites

def create_vibe_embedding(vibe):
    client = openai.OpenAI()  # Create an OpenAI client instance
    response = client.embeddings.create(input=[vibe], model=model_id)  # Create embedding for the vibe
    return response.data[0].embedding

def save_embeddings(embeddings, websites, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump((embeddings, websites), f)

def load_embeddings(file_path):
    with open(file_path, 'rb') as f:
        embeddings, websites = pickle.load(f)
    return embeddings, websites

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df.to_dict('records')

def calculate_scores(embeddings, vibe_embedding, websites, data):
    scores = []
    for hotel_name, embedding in embeddings.items(): 
        score = np.dot(embedding, vibe_embedding)  # Calculate the score
        website = websites.get(hotel_name, "")  # Get the website for the hotel, default to empty string if not found

        # Define default values for the additional fields
        city = rating = description = email_1 = website_description = subtypes = photo = 'N/A'

        # Check if the hotel name exists in the 'name' column of the data DataFrame
        if hotel_name in data['name'].values:
            hotel_data = data.loc[data['name'] == hotel_name].iloc[0]  # Get the first row of the DataFrame slice
            city = hotel_data['city']
            rating = hotel_data['rating']
            description = hotel_data['description']
            email_1 = hotel_data['email_1']
            website_description = hotel_data['website_description']
            subtypes = hotel_data['subtypes']
            # Check if the 'photo' column exists before trying to access it
            if 'photo' in hotel_data:
                photo = hotel_data['photo']  # Get the photo URL for the hotel

        # Append a score and the additional fields
        scores.append((hotel_name, score, website, city, rating, description, email_1, website_description, subtypes, photo))

    return scores

def rank_hotels(scores):
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def load_new_data(file_path):
    df = pd.read_csv(file_path)
    return df[['name', 'rooms', 'weekend_cost_feb']]

def load_or_create_embeddings(airtable_file, embeddings_file):
    if os.path.exists(embeddings_file):
        embeddings, websites = load_embeddings(embeddings_file)
    else:
        data = load_new_data(airtable_file)  # Use load_new_data instead of load_data
        embeddings, websites = create_embeddings(data.to_dict('records')) 

        # Save the embeddings to a new pickle file based on the selected CSV file
        if 'jn_improved_data.csv' in enriched_data_file:
            embeddings_file = './jn_improved_embeddings.pkl'
        else:
            embeddings_file = './new_saved_embeddings.pkl'
        save_embeddings(embeddings, websites, embeddings_file)

    return embeddings, websites

def main(vibe, csv_file):
    # Load the data from the CSV file
    data = pd.read_csv(csv_file)

    # Replace .csv with .pkl in the selected CSV file to get the embeddings file
    embeddings_file = csv_file.replace('.csv', '.pkl')

    # If the embeddings file does not exist, create it
    if not os.path.exists(embeddings_file):
        embeddings, websites = create_embeddings(data.to_dict('records'))
        save_embeddings(embeddings, websites, embeddings_file)
    else:
        embeddings, websites = load_embeddings(embeddings_file)

    vibe_embedding = create_vibe_embedding(vibe)
    scores = calculate_scores(embeddings, vibe_embedding, websites, data)
    ranked_scores = rank_hotels(scores)
    
    return ranked_scores, websites


# Load or create the embeddings once
airtable_file = './test_data.csv'
current_directory = os.getcwd()
embeddings_file = os.path.join(current_directory, 'new_saved_embeddings.pkl')

# # Use the embeddings for different 'vibe' inputs
# ranked_scores, websites = main('vibe1')
# for hotel_name, score in ranked_scores:
#     print(f'Hotel: {hotel_name}, Score: {score}, Website: {websites[hotel_name]}')
# # ...
# ranked_scores, websites = main('vibe2')
# for hotel_name, score in ranked_scores:
#     print(f'Hotel: {hotel_name}, Score: {score}, Website: {websites[hotel_name]}')