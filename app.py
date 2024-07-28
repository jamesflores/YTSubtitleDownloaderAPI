from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import JSONFormatter
from pytube import YouTube
import os
import logging

app = Flask(__name__)
CORS(app)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, World!")

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    youtube_url = request.args.get('url')
    if not youtube_url:
        abort(400, description="Missing YouTube URL")
    
    try:
        yt = YouTube(youtube_url)
        video_id = yt.video_id
    except Exception as e:
        logger.error(f"Error parsing YouTube URL: {str(e)}")
        abort(400, description="Invalid YouTube URL")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        json_transcript = JSONFormatter().format_transcript(transcript)
        logger.info(f"Successfully fetched transcript for video ID: {video_id}")
        return json_transcript, 200, {'Content-Type': 'application/json'}
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.warning(f"Transcript not available for video ID: {video_id}")
        abort(404, description="Transcript not available for this video")
    except Exception as e:
        logger.error(f"An error occurred while fetching transcript for video ID {video_id}: {str(e)}")
        abort(500, description=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)