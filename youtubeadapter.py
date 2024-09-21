from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from ratelimit import limits, sleep_and_retry
from scraperadapter import ScraperAdapter


class YouTubeAdapter(ScraperAdapter):
    def __init__(self, api_key):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        # self.raw_files = getfilelist('./raw/youtube/')

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

                    if self.isalreadypresent(video_id):
                        continue

                    video_info = self.youtube.videos().list(
                        part="snippet,statistics",
                        id=video_id
                    ).execute()['items'][0]

                    transcript = self.get_transcript(video_id)
                    comments = self.get_comments(video_id)

                    videos.append({
                        'video_id': video_id,
                        'title': video_info['snippet']['title'],
                        'description': video_info['snippet']['description'],
                        'channel': video_info['snippet']['channelTitle'],
                        'comments': comments,
                        'transcript': transcript
                    })

                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break

            except HttpError as e:
                print(f"An HTTP error {e.resp.status} occurred: {e.content}")
                break

            return videos

    def get_transcript(self, videoID):
        transcript = []

        try:
            transcripts = YouTubeTranscriptApi.get_transcript(videoID)

            for entry in transcripts:
                transcript.append(entry)

        except (NoTranscriptFound, TranscriptsDisabled):
            transcript = 'No transcript in en'

        except Exception as e:
            print(f"failed to fetch transcript for {videoID}: {e}")

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
            print(f"An HTTP error {e.resp.status} occurred while fetching comments: {e.content}")

        return comments

    def isalreadypresent(self, video_id):
        if f'{video_id}.json' in self.raw_files:
            return True

        return False

    def dumprawdata(self, videos):
        pass