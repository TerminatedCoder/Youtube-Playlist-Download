from pytube import Playlist, YouTube
import os
import re
import subprocess

def sanitize_filename(filename):
    # Remove or replace invalid characters for Windows file names
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube_playlist(playlist_url, output_path='downloads'):
    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Get the playlist
    playlist = Playlist(playlist_url)

    print(f'Downloading playlist: {sanitize_filename(playlist.title)}')

    # Iterate over all videos in the playlist with their index
    for index, video_url in enumerate(playlist.video_urls, start=1):
        yt = YouTube(video_url)
        sanitized_title = sanitize_filename(f'{index:03d} - {yt.title}')
        print(f'Downloading video: {sanitized_title}')

        # Try to get the highest resolution stream available (1080p)
        video_stream = yt.streams.filter(progressive=False, file_extension='mp4', res='1080p').first()
        
        # If 1080p is not available, try 720p
        if not video_stream:
            video_stream = yt.streams.filter(progressive=False, file_extension='mp4', res='720p').first()
        
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp3').first()

        if video_stream and audio_stream:
            try:
                video_file = video_stream.download(output_path, filename=sanitized_title + '.mp4')
                audio_file = audio_stream.download(output_path, filename=sanitized_title + '_audio.mp4')

                # Merge video and audio using ffmpeg
                output_file = os.path.join(output_path, sanitized_title + '_merged.mp4')
                command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c copy "{output_file}" -loglevel quiet'
                subprocess.run(command, shell=True, check=True)

                # Remove the separate audio and video files
                os.remove(video_file)
                os.remove(audio_file)
            except Exception as e:
                print(f"An error occurred while downloading {sanitized_title}: {e}")
        else:
            print(f'720p resolution or audio stream not available for video: {sanitized_title}')

if __name__ == '__main__':
    # Example playlist URL
    playlist_url = input("Enter the YouTube video URL: ")
    
    # Call the function to download the playlist
    download_youtube_playlist(playlist_url)
