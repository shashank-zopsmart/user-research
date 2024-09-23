import json
import csv
import os


def json_to_csv():
    # Read JSON data from file
    fileslist = os.listdir('./processed-transcripts/json')

    for file in fileslist:
        filename = file.split('.')[0]
        json_file_path = f'./processed-transcripts/json/{file}'
        csv_file_path = f'./processed-transcripts/csv/{filename}.csv'

        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Write JSON data to CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["quote", "code", "keywords"])
            writer.writeheader()
            for quote in data['quotes']:
                # Convert list of keywords to string
                quote['keywords'] = ', '.join(quote['keywords']) if isinstance(quote['keywords'], list) else quote[
                    'keywords']
                writer.writerow(quote)

        print(f"Data has been written to {csv_file_path}")