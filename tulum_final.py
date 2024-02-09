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
        websites[row['name']] = row['site']  # Map hotel name to website
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

        # Check if the hotel name exists in the 'name' column of the data DataFrame
        if hotel_name in data['name'].values:
            rooms = data.loc[data['name'] == hotel_name, 'rooms'].values[0]
            weekend_cost_feb = data.loc[data['name'] == hotel_name, 'weekend_cost_feb'].values[0]
        else:
            # If the hotel name doesn't exist, use default values
            rooms = 'N/A'
            weekend_cost_feb = 'N/A'

        # Only append a score if at least one of 'Rooms' and 'Per room cost' is not 'N/A'
        if rooms != 'N/A' or weekend_cost_feb != 'N/A':
            scores.append((hotel_name, score, website, rooms, weekend_cost_feb))  # Append a tuple of five elements
    return scores

def rank_hotels(scores):
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def load_new_data(file_path):
    df = pd.read_csv(file_path)
    return df[['name', 'rooms', 'weekend_cost_feb']]

def load_or_create_embeddings(airtable_file, embeddings_file, new_data_file):
    if os.path.exists(embeddings_file):
        embeddings, websites = load_embeddings(embeddings_file)
    else:
        data = load_data(airtable_file)
        new_data = load_new_data(new_data_file)
        data = pd.merge(data, new_data, on='name', how='left')
        embeddings, websites = create_embeddings(data.to_dict('records')) 
        save_embeddings(embeddings, websites, embeddings_file)
    return embeddings, websites

def main(vibe):
    embeddings, websites = load_or_create_embeddings(airtable_file, embeddings_file, enriched_data_file)
    data = pd.read_csv(enriched_data_file)
    vibe_embedding = create_vibe_embedding(vibe)
    scores = calculate_scores(embeddings, vibe_embedding, websites, data)
    ranked_scores = rank_hotels(scores)
    
    # Iterate over the ranked_scores list and print each hotel's name, score, website, rooms, and weekend_cost_feb
    for i, (hotel_name, score, website, rooms, weekend_cost_feb) in enumerate(ranked_scores, start=1):
        print(f'Hotel: {hotel_name}, Score: {score}, Website: {website}, Rooms: {rooms}, Weekend Cost Feb: {weekend_cost_feb}')
    
    return ranked_scores, websites

# Load or create the embeddings once
airtable_file = './test_data.csv'
current_directory = os.getcwd()
embeddings_file = os.path.join(current_directory, 'new_saved_embeddings.pkl')
enriched_data_file = './enriched_price_tulum_hotels.csv'


# # Use the embeddings for different 'vibe' inputs
# ranked_scores, websites = main('vibe1')
# for hotel_name, score in ranked_scores:
#     print(f'Hotel: {hotel_name}, Score: {score}, Website: {websites[hotel_name]}')
# # ...
# ranked_scores, websites = main('vibe2')
# for hotel_name, score in ranked_scores:
#     print(f'Hotel: {hotel_name}, Score: {score}, Website: {websites[hotel_name]}')