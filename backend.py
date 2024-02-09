from sentence_transformers import SentenceTransformer
from outscraper import ApiClient
import numpy as np
from pyairtable import Api
import time

#airtable tokens
airtable_access_token = 'patcjdHy5ZDwwTAHj.268de5ce676d56ee28e91baba8575111da66462312138864d8bc2836caecd0c9'
base_id = 'appvDNs9lOLRppHLl'
europe_hotels_table = 'europe_hotels'
api = Api(airtable_access_token) #for airtable API
# Import the Europe Hotels table from airtable
table = api.table(base_id, europe_hotels_table)

#outscraper tokens
outscraper_api_key = 'ZTUyODBkYmRlOTczNDI0ZTkzYzYwMWI3ZTQzZTk5NmZ8YTk4MzdlMGQ0OA'
client = ApiClient(api_key=outscraper_api_key) #for outscraper API

#Sentence Transformer model
model = SentenceTransformer("thenlper/gte-large") #Can change models, all-miniLM-L6-v2 is a the base model

def wait(seconds): #wait function
    time.sleep(seconds)

def query_exists_in_airtable(query): #checks if query exists in airtable
    records = table.all()  # Fetch all records from the table
    for record in records:
        if query.lower() == record['fields'].get('query', '').lower():
            return True  # Query found in Airtable
    return False  # Query does not exist in Airtable

def query_and_append(query, country_code): #gets the user input query, runs the outscraper API, and appends the results to airtable
    outscraper_results = []  # Initialize outscraper_results as an empty list
    #run outscraper query if the query doesn't already exist in airtable
    if not query_exists_in_airtable(query):
        outscraper_results = client.google_maps_search(query, limit=500, language='en', region=country_code ,enrichment='domains_service')
        #wait(10) #wait 5 seconds to make sure data gets appended to airtable

    # Parse the results from Outscraper and prepare them for batch creation in Airtable
    records_to_create = []
    # Iterate over each inner list in outscraper_results
    for place_list in outscraper_results:
        # Iterate over each dictionary in the inner list
        for result in place_list:
            # Create a dictionary for each result with the fields you want to include
            record = {
                'query': result.get('query', ''),
                'name': result.get('name', ''),
                'place_id': result.get('place_id', ''),
                'full_address': result.get('full_address', ''),
                'country': result.get('country', ''),
                'city': result.get('city', ''),
                'site': result.get('site', ''),
                'type': result.get('type', ''),
                'description': result.get('description', ''),
                'category': result.get('category', ''),
                'subtypes': result.get('subtypes', ''),
                'rating': result.get('rating', ''),
                'reviews': result.get('reviews', ''),
                'reviews_link': result.get('reviews_link', ''),
                'photo': result.get('photo', ''),
                'range': result.get('range', ''),
                'email_1': result.get('email_1', ''),
                'email_2': result.get('email_2', ''),
                'email_3': result.get('email_3', ''),
                'instagram': result.get('instagram', ''),
                'website_title': result.get('website_title', ''),
                'website_description': result.get('website_description', ''),
            }
            records_to_create.append(record)
            
    # Batch create records in Airtable
    if records_to_create:
        table.batch_create(records_to_create)
        #might also want to append to my global list of records
    return records_to_create


def fetch_and_prepare_data():
    
    # Import all the records from the table
    records = table.all()

    # Filter records to include only those with a rating of 4.5 or higher
    filtered_records = [record for record in records if float(record['fields'].get('rating', 0)) >= 4.5]

    # Get all the descriptions as a list
    descriptions = [record['fields'].get('description', '') for record in filtered_records]
    # Do the same thing but for the hotel names
    hotel_name = [record['fields'].get('name', '') for record in filtered_records]
    # Do the same thing but for the site
    hotel_website = [record['fields'].get('site', '') for record in filtered_records]
    # Do the same thing but for email_1
    hotel_email = [record['fields'].get('email_1', '') for record in filtered_records]
    # Do the same thing but for rating
    hotel_rating = [record['fields'].get('rating', '') for record in filtered_records]
    # Do the same thing but for city
    hotel_city = [record['fields'].get('city', '') for record in filtered_records]

    # Descriptions are encoded by calling model.encode()
    description_embeddings = model.encode(descriptions)

    return filtered_records, descriptions, hotel_name, hotel_website, hotel_email, hotel_rating, hotel_city, description_embeddings


def main(query, country_code, vibe): #query, country_code, and vibe from user input
    filtered_records, descriptions, hotel_name, hotel_website, hotel_email, hotel_rating, hotel_city, description_embeddings = fetch_and_prepare_data()
    vibe = model.encode(vibe)
    scores = [] #create an empty list to store the scores
    #for each embedding, compute the dot product with the vibe.
    for embedding in description_embeddings: 
       score = (np.dot(vibe, embedding))
       scores.append(score)

    #create a similar dictionary for the hotel names and the sites
    hotel_output = []
    for name, site, email, score, rating, city in zip(hotel_name, hotel_website, hotel_email, scores, hotel_rating, hotel_city):
        hotel_output.append({'hotel_name': name, 'website': site, 'email': email, 'score': score, 'rating': rating, 'city': city})
    # Sort the hotel names and sites and emails by their score
    hotel_output = sorted(hotel_output, key=lambda x: x['score'], reverse=True)
    #but return the hotel names and sites and emails as values
    return hotel_output