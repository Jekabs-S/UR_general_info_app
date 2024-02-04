import requests
import json
import time
import os
from datetime import datetime
import concurrent.futures
import numpy as np
import pandas as pd

def fetch_data_for_entity_names(entity_names):
    # Endpoint URL
    url = "https://data.gov.lv/dati/api/3/action/datastore_search"

    # Define a mapping from API field names to database field names
    field_mapping = {
        'regcode': 'regcode',
        'sepa': 'sepa',
        'name': 'name',
        'regtype_text': 'regtype_text',
        'type': 'type',
        'type_text': 'type_text',   
        'registered': 'date_registered',
        'terminated': 'date_terminated',
        'closed': 'closed',
        'address': 'address',
        'index': 'post_index',
    }

    records = []

    # Loop through each entity_name and make a request to the API
    for entity_name in entity_names:
        print(f"Processing entity_name {entity_name}")
        for attempt in range(3):  # Retry up to 3 times
            try:
                # Parameters for the request, including the resource_id and filter for regcode
                params = {
                    "resource_id": "25e80bf3-f107-4ab4-89ef-251b5b9374e9",
                    "filters": json.dumps({"name": str(entity_name)})
                }

                # Making the request to the CKAN API
                response = requests.get(url, params=params)

                # Checking if the request was successful
                if response.status_code == 200:
                    # Parse the response and store the data
                    data = response.json()['result']['records']

                    # Create a new dictionary with the database field names
                    for record in data:
                        db_record = {}
                        for api_field, db_field in field_mapping.items():
                            if api_field in record and record[api_field]:
                                if api_field in ['registered', 'terminated']:
                                    # Convert date strings to datetime objects
                                    db_record[db_field] = datetime.strptime(record[api_field], '%Y-%m-%dT%H:%M:%S')
                                else:
                                    db_record[db_field] = record[api_field]
                        records.append(db_record)

                # If the request was successful, break out of the retry loop
                break
            except:
                # If the request failed, wait a bit before retrying
                print(f"Attempt {attempt+1} failed for entity_name {entity_name}. Retrying in 5 seconds...")
                time.sleep(5)

    return records

def fetch_and_insert_data(entity_names):
    # Split the entity_name values into 8 equal parts
    entity_name_parts = np.array_split(entity_names, 8)

    # Fetch the data in parallel using 8 threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(fetch_data_for_entity_names, entity_name_parts))

    # Flatten the list of records
    records = [record for part in records for record in part]

    return records

def main(file):
    # Check if the input file exists
    if not os.path.isfile(file):
        print(f"Error: File {file} does not exist.")
        return

    # Read the entity name from the uploaded file
    try:
        df = pd.read_excel(file)
    except Exception as e:
        print(f"Error: Failed to read file {file}. {str(e)}")
        return

    # Check if the 'entity_name' column exists in the file
    if 'entity_name' not in df.columns:
        print("Error: 'entity_name' column not found in the input file.")
        return

    entity_names = df['entity_name'].tolist()

    try:
        records = fetch_and_insert_data(entity_names)
    except Exception as e:
        print(f"Error: Failed to fetch data for entity name. {str(e)}")
        return

    # Convert the records to a DataFrame and save it to a new .xlsx file
    try:
        df = pd.DataFrame(records)
        df.to_excel('entity_ur_data.xlsx', index=False)
    except Exception as e:
        print(f"Error: Failed to save data to 'entity_ur_data.xlsx'. {str(e)}")

if __name__ == "__main__":
    start_time = time.time()
    main('input.xlsx')  # replace 'input.xlsx' with the path to your input file
    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time} seconds")
print("Done")