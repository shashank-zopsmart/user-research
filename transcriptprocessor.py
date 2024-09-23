import json
from pydantic import BaseModel, ValidationError
import os
from openai import OpenAI, OpenAIError
from loguru import logger


class QuoteSchema(BaseModel):
    quote: str
    code: str
    keywords: list[str]


class AnalysisSchema(BaseModel):
    codes: list[str]
    keywords: list[str]
    quotes: list[QuoteSchema]


class TranscriptProcessor:
    def __init__(self, openai_api_key, transcript_source, raw_files):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.transcript_source = transcript_source
        self.raw_files = raw_files
        self.processed_transcripts = os.listdir('./processed-transcripts/')

    def process_transcripts(self):
        for raw_file in self.raw_files:
            try:
                if f"{self.transcript_source}-{raw_file}" in self.processed_transcripts:
                    continue

                filepath = f"./raw/{self.transcript_source}/{raw_file}"
                try:
                    with open(filepath, 'r') as file:
                        transcript = file.read()
                except FileNotFoundError:
                    logger.warning(f"The file {filepath} was not found.")
                    continue
                except IOError as e:
                    logger.error(f"An I/O error occurred while reading the file {filepath}: {e}")
                    continue

                try:
                    analysis = self.analyze_transcript_in_batches(transcript)
                    self.save_response(raw_file, analysis)
                    self.processed_transcripts.append(f"{self.transcript_source}-{raw_file}")

                    logger.info(
                        f"Transcript analysis complete for {raw_file}. Check processed-transcripts directory for the results.")
                except Exception as e:
                    logger.error(f"An error occurred during transcript analysis for file {raw_file}: {e}")
                    continue
            except Exception as e:
                logger.error(f"An unexpected error occurred during processing file {raw_file}: {e}")

    def analyze_transcript_in_batches(self, transcript):
        tokens = transcript.split()
        batch_size = 10000
        responses = []

        for i in range(0, len(tokens), batch_size):
            batch_tokens = tokens[i:i + batch_size]
            batch_transcript = ' '.join(batch_tokens)

            try:
                response = self.analyze_transcript(batch_transcript)
                if response:
                    responses.append(response)
            except OpenAIError as e:
                logger.error(f"An error occurred during the API call: {e}")
                continue

        combined_response = self.combine_responses(responses)
        return combined_response

    def analyze_transcript(self, transcript):
        try:
            messages = [
                {"role": "system",
                 "content": "You are a qualitative research expert. Extract key phrases, quotes, keywords, and group them into suitable themes with codes."},
                {"role": "user", "content": f"Here is the transcript: {transcript}"}
            ]
            response = self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-mini-2024-07-18",
                messages=messages,
                max_tokens=10000,
                temperature=0.5,
                response_format=AnalysisSchema,
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            logger.error(f"An error occurred with the OpenAI API: {e}")
            raise e

    def combine_responses(self, responses):
        combined_data = {
            'codes': [],
            'keywords': [],
            'quotes': []
        }
        for response in responses:
            try:
                analysis_data = AnalysisSchema(**json.loads(response))

                combined_data['codes'].extend(analysis_data.codes)
                combined_data['keywords'].extend(analysis_data.keywords)
                combined_data['quotes'].extend(analysis_data.quotes)

            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"An error occurred while parsing the response: {e}")

        return combined_data

    def save_response(self, filename, data):
        filename = f'./processed-transcripts/{self.transcript_source}-{filename}'
        try:
            with open(filename, 'w') as f:
                f.write(json.dumps(data, indent=4))
            logger.info(f'Data has been successfully written to {filename}')
        except IOError as e:
            logger.error(f'An I/O error occurred while writing the file: {e}')
        except json.JSONDecodeError as e:
            logger.error(f'An error occurred while encoding JSON: {e}')
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
