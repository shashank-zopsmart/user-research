import csv
import json
import os
from loguru import logger


def segment_transcript_json_to_csv():
    fieldnames = [
        'id', 'source', 'url', 'segment_index', 'segment_topic',
        'segment_start_time', 'segment_end_time', 'segment_content'
    ]

    json_directory = "./processed-transcripts/json/segment_transcript"
    output_csv_file_path = "./processed-transcripts/csv/segment_transcript"

    os.makedirs(output_csv_file_path, exist_ok=True)

    output_csv_file = f'{output_csv_file_path}/segment_transcript.csv'

    try:
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for json_file in os.listdir(json_directory):
                if json_file.endswith('.json'):
                    file_path = os.path.join(json_directory, json_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            for index, segment in enumerate(data.get('segments', [])):
                                for content in segment.get('content', []):
                                    row = {
                                        'id': data.get('id'),
                                        'source': data.get('source'),
                                        'url': data.get('url'),
                                        'segment_index': index,
                                        'segment_topic': segment.get('topic'),
                                        'segment_start_time': segment.get('start_time'),
                                        'segment_end_time': segment.get('end_time'),
                                        'segment_content': content
                                    }
                                    writer.writerow(row)
                        logger.info(f"Successfully processed file: {json_file}")

                    except json.JSONDecodeError:
                        logger.error(f"JSON decoding failed for file: {file_path}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing file {file_path}: {e}")

    except IOError as e:
        logger.critical(f"Failed to write CSV file: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")


def open_coding_json_to_csv():
    fieldnames = [
        "id", "source", "url",
        "segment_start", "segment_end", "segment_text",
        "significant_words", "initial_codes"
    ]

    json_directory = "./processed-transcripts/json/open_coding"
    output_csv_file_path = "./processed-transcripts/csv/open_coding"

    os.makedirs(output_csv_file_path, exist_ok=True)

    output_csv_file = f'{output_csv_file_path}/open_coding.csv'

    try:
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for json_file in os.listdir(json_directory):
                if json_file.endswith('.json'):
                    file_path = os.path.join(json_directory, json_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            for ele in data:
                                for segment in ele.get('segments', []):
                                    row = {
                                        'id': ele.get('id', ''),
                                        'source': ele.get('source', ''),
                                        'url': ele.get('url', ''),
                                        'segment_start': segment.get('start', ''),
                                        'segment_end': segment.get('end', ''),
                                        'segment_text': segment.get('text', ''),
                                        'significant_words': ', '.join(segment.get('significant_words', [])),
                                        'initial_codes': ', '.join(segment.get('initial_codes', []))
                                    }
                                    writer.writerow(row)

                        logger.info(f"Successfully processed file: {json_file}")

                    except json.JSONDecodeError:
                        logger.error(f"JSON decoding failed for file: {file_path}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing file {file_path}: {e}")

    except IOError as e:
        logger.critical(f"Failed to write CSV file: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")


def themes_json_to_csv():
    fieldnames = [
        "id", "source", "url", "theme_name", "code"
    ]

    json_directory = "./processed-transcripts/json/clustering_and_thematic_analysis"
    output_csv_file_path = "./processed-transcripts/csv/clustering_and_thematic_analysis"

    os.makedirs(output_csv_file_path, exist_ok=True)

    output_csv_file = f'{output_csv_file_path}/themes.csv'

    try:
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for json_file in os.listdir(json_directory):
                if json_file.endswith('.json'):
                    file_path = os.path.join(json_directory, json_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            for theme_name, theme_data in data.get('themes', {}).items():
                                codes = theme_data.get('codes', [])
                                for code in codes:
                                    row = {
                                        'id': data.get('id', ''),
                                        'source': data.get('source', ''),
                                        'url': data.get('url', ''),
                                        'theme_name': theme_name,
                                        'code': code
                                    }
                                    writer.writerow(row)

                        logger.info(f"Successfully processed file: {json_file}")

                    except json.JSONDecodeError:
                        logger.error(f"JSON decoding failed for file: {file_path}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing file {file_path}: {e}")

    except IOError as e:
        logger.critical(f"Failed to write CSV file: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")


import os
import csv
import json
import logging


def affinity_map_and_user_personas_json_to_csv():
    affinity_fieldnames = [
        "id", "source", "url", "theme_name", "code"
    ]

    user_personas_fieldnames = [
        "id", "source", "url", "persona_name", "age", "role",
        "goals", "challenges", "motivations"
    ]

    json_directory = "./processed-transcripts/json/affinity_mapping_and_persona_development"
    output_csv_file_path = "./processed-transcripts/csv/affinity_mapping_and_persona_development"

    os.makedirs(output_csv_file_path, exist_ok=True)

    affinity_csv_file = f'{output_csv_file_path}/affinity_map.csv'
    user_personas_csv_file = f'{output_csv_file_path}/user_personas.csv'

    try:
        with open(affinity_csv_file, mode='w', newline='', encoding='utf-8') as affinity_file, \
                open(user_personas_csv_file, mode='w', newline='', encoding='utf-8') as personas_file:

            affinity_writer = csv.DictWriter(affinity_file, fieldnames=affinity_fieldnames)
            personas_writer = csv.DictWriter(personas_file, fieldnames=user_personas_fieldnames)

            affinity_writer.writeheader()
            personas_writer.writeheader()

            for json_file in os.listdir(json_directory):
                if json_file.endswith('.json'):
                    file_path = os.path.join(json_directory, json_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            # Write affinity_map data to CSV
                            for theme_name, theme_data in data.get('affinity_map', {}).items():
                                codes = theme_data.get('codes', [])
                                for code in codes:
                                    affinity_row = {
                                        'id': data.get('id', ''),
                                        'source': data.get('source', ''),
                                        'url': data.get('url', ''),
                                        'theme_name': theme_name,
                                        'code': code
                                    }
                                    affinity_writer.writerow(affinity_row)

                            # Write user_personas data to CSV
                            for persona in data.get('user_personas', []):
                                personas_row = {
                                    'id': data.get('id', ''),
                                    'source': data.get('source', ''),
                                    'url': data.get('url', ''),
                                    'persona_name': persona.get('name', ''),
                                    'age': persona.get('age', ''),
                                    'role': persona.get('role', ''),
                                    'goals': ', '.join(persona.get('goals', [])),
                                    'challenges': ', '.join(persona.get('challenges', [])),
                                    'motivations': ', '.join(persona.get('motivations', []))
                                }
                                personas_writer.writerow(personas_row)

                        logger.info(f"Successfully processed file: {json_file}")

                    except json.JSONDecodeError:
                        logger.error(f"JSON decoding failed for file: {file_path}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing file {file_path}: {e}")

    except IOError as e:
        logger.critical(f"Failed to write CSV file: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")


import os
import csv
import json
import logging


def process_json_to_csv():
    affinity_fieldnames = ["id", "source", "url", "section", "theme_name", "code"]
    user_personas_fieldnames = ["id", "source", "url", "persona_name", "age", "role",
                                "goals", "challenges", "motivations"]

    json_directory = "./processed-transcripts/json/validate_and_document"
    output_csv_file_path = "./processed-transcripts/csv/validate_and_document"

    os.makedirs(output_csv_file_path, exist_ok=True)

    affinity_csv_file = f'{output_csv_file_path}/affinity_map.csv'
    user_personas_csv_file = f'{output_csv_file_path}/user_personas.csv'

    try:
        with open(affinity_csv_file, mode='w', newline='', encoding='utf-8') as affinity_file, \
                open(user_personas_csv_file, mode='w', newline='', encoding='utf-8') as personas_file:

            affinity_writer = csv.DictWriter(affinity_file, fieldnames=affinity_fieldnames)
            personas_writer = csv.DictWriter(personas_file, fieldnames=user_personas_fieldnames)

            affinity_writer.writeheader()
            personas_writer.writeheader()

            for json_file in os.listdir(json_directory):
                if json_file.endswith('.json'):
                    file_path = os.path.join(json_directory, json_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            common_fields = {
                                'id': data.get('id', ''),
                                'source': data.get('source', ''),
                                'url': data.get('url', '')
                            }

                            def process_affinity_map(section, section_data):
                                for theme_name, theme_data in section_data.items():
                                    codes = theme_data.get('codes', [])
                                    for code in codes:
                                        row = dict(common_fields, section=section, theme_name=theme_name, code=code)
                                        affinity_writer.writerow(row)

                            # Write affinity_map and clusters data to CSV
                            process_affinity_map("affinity_map",
                                                 data.get('review', {}).get('personas', {}).get('affinity_map', {}))
                            process_affinity_map("clusters",
                                                 data.get('review', {}).get('clusters', {}).get('themes', {}))

                            # Write user_personas data to CSV
                            for persona in data.get('review', {}).get('personas', {}).get('user_personas', []):
                                row = dict(common_fields,
                                           persona_name=persona.get('name', ''),
                                           age=persona.get('age', ''),
                                           role=persona.get('role', ''),
                                           goals=', '.join(persona.get('goals', [])),
                                           challenges=', '.join(persona.get('challenges', [])),
                                           motivations=', '.join(persona.get('motivations', []))
                                           )
                                personas_writer.writerow(row)

                        logger.info(f"Successfully processed file: {json_file}")

                    except json.JSONDecodeError:
                        logger.error(f"JSON decoding failed for file: {file_path}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing file {file_path}: {e}")

    except IOError as e:
        logger.critical(f"Failed to write CSV file: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")


def json_to_csv():
    segment_transcript_json_to_csv()
    open_coding_json_to_csv()
    themes_json_to_csv()
    affinity_map_and_user_personas_json_to_csv()
    process_json_to_csv()
