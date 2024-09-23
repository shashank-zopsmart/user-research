import json
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from ratelimit import limits, sleep_and_retry
from scraperadapter import ScraperAdapter
from loguru import logger


class YouTubeAdapter(ScraperAdapter):
    def __init__(self, api_key, threshold_criteria=None):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.scraped_videos = os.listdir('./raw/youtube/')
        self.threshold_criteria = threshold_criteria

    @sleep_and_retry
    @limits(calls=100, period=100)
    def scrape(self, query, max_results=50):
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            try:
                search_response = self.youtube.search().list(
                    q=query,
                    type="video",
                    part="id,snippet",
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()

                for item in search_response.get('items', []):
                    video_id = item['id']['videoId']

                    if f'{video_id}.json' in self.scraped_videos:
                        continue

                    video_info = self.youtube.videos().list(
                        part="snippet,statistics",
                        id=video_id
                    ).execute()['items'][0]

                    if self.threshold_criteria and not self.threshold_criteria(video_info):
                        continue

                    transcript = self.get_transcript(video_id)
                    comments = self.get_comments(video_id)

                    video_data = {
                        'video_id': video_id,
                        'title': video_info['snippet']['title'],
                        'description': video_info['snippet']['description'],
                        'channel': video_info['snippet']['channelTitle'],
                        'likes': video_info['statistics'].get('likeCount', 0),
                        'views': video_info['statistics'].get('viewCount', 0),
                        'comments': comments,
                        'transcript': transcript
                    }

                    self.save_response(video_id, video_data)
                    self.scraped_videos.append(f'{video_id}.json')
                    videos.append(video_data)

                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break

            except HttpError as e:
                logger.error(f"An HTTP error {e.resp.status} occurred: {e.content}")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                break

        logger.info('Scraping completed successfully.')
        return self.scraped_videos

    def get_transcript(self, video_id):
        transcript = []

        try:
            transcripts = YouTubeTranscriptApi.get_transcript(video_id)

            for entry in transcripts:
                transcript.append(entry)

        except (NoTranscriptFound, TranscriptsDisabled):
            transcript = 'No transcript available'
            logger.warning(f"No transcript available for video {video_id}")

        except Exception as e:
            logger.error(f"Failed to fetch transcript for {video_id}: {e}")

        return transcript

    def get_comments(self, video_id, max_comments=5):
        comments = []
        try:
            comments_response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_comments
            ).execute()

            for comment_item in comments_response.get('items', []):
                top_comment = comment_item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': top_comment['authorDisplayName'],
                    'text': top_comment['textDisplay'],
                    'likeCount': top_comment['likeCount']
                })

        except HttpError as e:
            logger.error(f"An HTTP error {e.resp.status} occurred while fetching comments: {e.content}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching comments: {e}")

        return comments

    def save_response(self, video_id, data):
        filename = f'./raw/youtube/{video_id}.json'
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f'Data has been successfully written to {filename}')
        except IOError as e:
            logger.error(f'An I/O error occurred while writing the file: {e}')
        except json.JSONDecodeError as e:
            logger.error(f'An error occurred while encoding JSON: {e}')
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
