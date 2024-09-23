from pytube import YouTube
import os


class YouTubeAudioDownloader:
    def __init__(self, download_path="downloads"):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    def fetch_audio(self, video_url):
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_url}")
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream:
                output_file = audio_stream.download(output_path=self.download_path)
                base, ext = os.path.splitext(output_file)
                new_file = base + '.mp3'
                os.rename(output_file, new_file)
                print(f"Audio file downloaded and saved as {new_file}")
                return new_file
            else:
                print("No audio stream available for this video.")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None