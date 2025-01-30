import pandas as pd
from sqlalchemy import create_engine, values

host = "localhost"
port = "5432"
database = "SportRadar_db"
user = "postgres"
password = "1418"

# Create the connection string (URL format) -> postgres

engine_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(engine_string)

#####################################################################################################

####################### 1) COLLECT THE COMPETITION DATA FROM THE API ENDPOINTS ######################

# Description: This script collects data from the SportRadar API endpoints and saves the data to a PostgreSQL database.

import requests

url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=b7Lb8YowaJBzkWHZ2RWgXCcxf3mMnF2JuojMp6d5"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

# Convert the response to json

json_data = response.json()

# Convert nested json to dataframe

# Competition data

competition_data = pd.json_normalize(json_data,['competitions'])

# Categories data

categories_df = pd.json_normalize(json_data['competitions'], record_path=None, meta=['id'], sep='_')

# Rename columns in competition_data for clarity

competition_data.rename(columns={'id': 'competition_id', 'name': 'competition_name'}, inplace=True)

# Rename columns in categories_df for clarity

categories_df.rename(columns={'category.id': 'category_id', 'category.name': 'category_name'}, inplace=True)

# Drop the 'category' column from competitions_df to avoid redundancy

competition_data.drop(columns=['category.name','level'], inplace=True)

# Drop the 'competitions' column from categories_df to avoid redundancy

categories_df.drop(columns=['id','name','level','gender','type','parent_id'], inplace=True)

#####################################################################################################

####################### 2) COLLECT THE COMPLEXES DATA FROM THE API ENDPOINTS ########################

# Description: This script collects data from the SportRadar API endpoints and saves the data to a PostgreSQL database.

url1 = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=b7Lb8YowaJBzkWHZ2RWgXCcxf3mMnF2JuojMp6d5"

response_complex = requests.get(url1, headers=headers)

# Convert the response to json

json_data_complexes = response_complex.json()

# print(json_data_complexes)

# Convert nested json to dataframe

df = pd.DataFrame(json_data_complexes['complexes'], columns=['id', 'name', 'venues'])

df_exploded = df.explode("venues")
venues_df = pd.json_normalize(df_exploded["venues"])

# Ensure the index is unique before concatenating

complex_data = df_exploded.reset_index(drop=True)

# rename columns in the complex_data dataframe for clarity

complex_data.rename(columns={"id": "complex_id", "name": "complex_name"}, inplace=True)

venues_df = venues_df.reset_index(drop=True)

# Rename columns in the final dataframe for clarity

venues_df.rename(columns={"id": "venue_id", "name": "venue_name"}, inplace=True)

# Concatenate the dataframes
   
venue_data = pd.concat([complex_data.drop(columns=["venues"]), venues_df], axis=1)

# move the complex_id and complex_name columns to the front of the dataframe

complex_data.drop(columns=["venues"], inplace=True)

# move the venue_id,venue_name,city_name,country_name,country_code,timezone columns to the front of the dataframe

venue_data.drop(columns=['capacity', 'map_coordinates','complex_name',], inplace=True)

######################################################################################################

############### 3) COLLECT THE DOUBLES COMPETITOR RANKINGS DATA FROM THE API ENDPOINTS ###############

# Description: This script collects data from the SportRadar API endpoints and saves the data to a PostgreSQL database.

url2 = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=b7Lb8YowaJBzkWHZ2RWgXCcxf3mMnF2JuojMp6d5"

response_competitor = requests.get(url2, headers=headers)

# Convert the response to json

json_data_competitors = response_competitor.json()

# Convert nested json to dataframe

competitors_ranking = pd.DataFrame(json_data_competitors['rankings'], 
                                   columns=['rank', 'competitor_rankings', 'competitor'])

competitors_ranking_exp = competitors_ranking.explode("competitor_rankings")

ranking = pd.json_normalize(competitors_ranking_exp["competitor_rankings"])
competitor_df = pd.json_normalize(competitors_ranking_exp["competitor_rankings"])

# drop the 'competitor_rankings' column from the df_competitors_exploded dataframe to avoid redundancy

ranking.drop(columns=['competitor.name', 'competitor.country', 'competitor.country_code',
                     'competitor.abbreviation'], inplace=True)
ranking.rename(columns={'competitor.id': 'competitor_id'}, inplace=True)

# drop the 'rankings' column from the competitor_df dataframe to avoid redundancy

competitor_df.drop(columns=['rank', 'movement', 'points', 'competitions_played'], inplace=True)
competitor_df.rename(columns={'competitor.id': 'competitor_id', 'competitor.name': 'name',
                                        'competitor.country': 'country', 
                                        'competitor.country_code': 'country_code',
                                        'competitor.abbreviation': 'abbreviation'}, inplace=True)

try:

######################## Save the data to the database into corresponding tables #######################
   
#  Move the data to the competition,categories tables

    competition_data.to_sql('competitions', engine, if_exists='replace', index=False)
    categories_df.to_sql('categories', engine, if_exists='replace', index=False)

#  Move the data to the complex,venue tables

    complex_data.to_sql('complexes', engine, if_exists='replace', index=False)
    venue_data.to_sql('venues', engine, if_exists='replace', index=False)

#  Move the data to the ranking,competitor tables

    ranking.to_sql('rankings', engine, if_exists='replace', index=False)
    competitor_df.to_sql('competitors', engine, if_exists='replace', index=False)

# Print a success message if the data is saved successfully

    print("Data successfully inserted into the corresponding database.")

# Print an error message if the data is not saved successfully

except Exception as e:
    
    print("An error occurred while inserting data into the database.")  

# Close the database connection

engine.dispose()

######################################################################################################



