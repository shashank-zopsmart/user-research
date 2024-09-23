import json
import os
from openai import OpenAI, OpenAIError
from loguru import logger

from models import *


class TranscriptProcessor:
    def __init__(self, openai_api_key: str, transcript_source: str, raw_files: List[str]):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.transcript_source = transcript_source
        self.raw_files = raw_files
        self.processed_transcripts = os.listdir('./processed-transcripts/json')
        self.urls = {
            'youtube': 'https://www.youtube.com/watch?v={}'
        }

    def process_transcripts(self):
        for raw_file in self.raw_files:
            if f"{self.transcript_source}-{raw_file}" in self.processed_transcripts:
                continue

            filepath = f"./raw/{self.transcript_source}/{raw_file}"
            try:
                with open(filepath, 'r') as file:
                    transcript = file.read()
                analysis_result = self.analyze_transcript(transcript, raw_file)
                self.save_response(raw_file, analysis_result)
                logger.info(
                    f"Transcript analysis complete for {raw_file}. Check processed-transcripts directory for the results.")
            except (FileNotFoundError, IOError, OpenAIError, Exception) as e:
                logger.exception(f"An error occurred while processing file {raw_file}: {e}")

    def analyze_transcript(self, transcript: str, raw_file: str) -> Dict[str, Any]:
        segments = self.segment_transcript(transcript, raw_file)
        codes = self.open_coding(segments, raw_file)
        clusters = self.clustering_and_thematic_analysis(codes, raw_file)
        personas = self.affinity_mapping_and_persona_development(clusters, raw_file)
        validated_data = self.validate_and_document(personas, clusters, raw_file)
        return validated_data

    def segment_transcript(self, transcript: str, raw_file: str) -> List[Dict[str, Any]]:
        """Step 1: Familiarization and Segmentation"""
        # Send prompt 1 to API
        messages = [
            {"role": "system",
             "content": "You are a qualitative research expert. Please read the transcript and divide it into meaningful segments based on changes in topic, speaker, or activity. Give response in JSON."},
            {"role": "user", "content": transcript}
        ]
        response = self._api_call(messages)
        segments = json.loads(response.choices[0].message.content)
        segments['id'] = raw_file.split(".")[0]
        segments['source'] = self.transcript_source
        segments['url'] = self.urls[self.transcript_source].format(raw_file.split(".")[0])
        self.save_response(raw_file, segments, "segment_transcript")
        return segments

    def open_coding(self, segments: List[Dict[str, Any]], raw_file: str) -> List[Dict[str, Any]]:
        """Step 2: Open Coding"""
        codes = []
        for segment in segments['segments']:
            messages = [
                {"role": "system",
                 "content": "You are a qualitative research expert. Identify significant words, phrases, or sentences in each segment that capture key ideas or concepts and assign initial codes. Give response in JSON."},
                {"role": "user", "content": json.dumps(segment)}
            ]
            response = self._api_call(messages)
            segment_codes = json.loads(response.choices[0].message.content)
            segment_codes['id'] = raw_file.split(".")[0]
            segment_codes['source'] = self.transcript_source
            segment_codes['url'] = self.urls[self.transcript_source].format(raw_file.split(".")[0])
            codes.append(segment_codes)

        self.save_response(raw_file, codes, "open_coding")
        return codes

    def clustering_and_thematic_analysis(self, codes: List[Dict[str, Any]], raw_file: str) -> List[Dict[str, Any]]:
        """Step 3: Clustering Codes and Thematic Analysis"""
        messages = [
            {"role": "system",
             "content": "You are a qualitative research expert. Group similar or related codes together to form clusters and identify overarching themes. Give response in JSON."},
            {"role": "user", "content": json.dumps(codes)}
        ]
        response = self._api_call(messages)
        clusters = json.loads(response.choices[0].message.content)
        clusters['id'] = raw_file.split(".")[0]
        clusters['source'] = self.transcript_source
        clusters['url'] = self.urls[self.transcript_source].format(raw_file.split(".")[0])
        self.save_response(raw_file, clusters, "clustering_and_thematic_analysis")
        return clusters

    def affinity_mapping_and_persona_development(self, clusters: List[Dict[str, Any]], raw_file: str) -> List[Dict[str, Any]]:
        messages = [
            {"role": "system",
             "content": "You are a qualitative research expert. Using the identified themes, create an affinity map and develop user personas. Give response in JSON."},
            {"role": "user", "content": json.dumps(clusters)}
        ]
        response = self._api_call(messages)
        personas = json.loads(response.choices[0].message.content)
        personas['id'] = raw_file.split(".")[0]
        personas['source'] = self.transcript_source
        personas['url'] = self.urls[self.transcript_source].format(raw_file.split(".")[0])
        self.save_response(raw_file, personas, "affinity_mapping_and_persona_development")
        return personas

    def validate_and_document(self, personas: List[Dict[str, Any]], clusters: List[Dict[str, Any]], raw_file: str) -> Dict[str, Any]:
        messages = [
            {"role": "system",
             "content": "You are a qualitative research expert. Review the personas and themes to ensure they accurately reflect the data and context of the transcript. Give response in JSON."},
            {"role": "user", "content": json.dumps({"personas": personas, "clusters": clusters})}
        ]
        response = self._api_call(messages)
        validated_data = json.loads(response.choices[0].message.content)
        validated_data['id'] = raw_file.split(".")[0]
        validated_data['source'] = self.transcript_source
        validated_data['url'] = self.urls[self.transcript_source].format(raw_file.split(".")[0])
        self.save_response(raw_file, validated_data, "validate_and_document")
        return validated_data

    def _api_call(self, messages: List[Dict[str, Any]], response_format=None) -> Dict[str, Any]:
        try:
            response_format = { "type": "json_object" } if response_format == None else response_format
            response = self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-mini-2024-07-18",
                messages=messages,
                max_tokens=10000,
                temperature=0.5,
                response_format=response_format,
            )
            return response
        except OpenAIError as e:
            logger.exception(f"An error occurred with the OpenAI API: {e}")
            raise e

    def save_response(self, filename: str, data: Dict[str, Any], step: str = None):
        filepath = f'./processed-transcripts/json/' if step is None else f'./processed-transcripts/json/{step}/'

        os.makedirs(filepath, exist_ok=True)

        filename = f'{filepath}/{self.transcript_source}-{filename}'
        try:
            with open(filename, 'w+') as f:
                f.write(json.dumps(data, indent=4, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o)))
            logger.info(f'Data has been successfully written to {filename}')
        except IOError as e:
            logger.exception(f'An I/O error occurred while writing the file: {e}')
        except json.JSONDecodeError as e:
            logger.exception(f'An error occurred while encoding JSON: {e}')
        except Exception as e:
            logger.exception(f'An unexpected error occurred: {e}')
