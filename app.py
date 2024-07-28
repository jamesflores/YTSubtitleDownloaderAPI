from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import JSONFormatter
from pytube import YouTube
import os
import logging

app = Flask(__name__)
CORS(app)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, World!")

@app.route('/api/transcript', methods=['GET'])
@limiter.limit("10 per minute")   # add a specific rate limit for this endpoint
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

@app.route('/openapi.json', methods=['GET'])
def get_openapi_schema():
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "YouTube Transcript API",
            "description": "Retrieves transcript data for YouTube videos.",
            "version": "v1.0.0"
        },
        "servers": [
            {
                "url": request.url_root.rstrip('/').replace('http://', 'https://')   # use the current server's URL with https
            }
        ],
        "paths": {
            "/api/transcript": {
                "get": {
                    "description": "Get transcript for a specific YouTube video",
                    "operationId": "GetYouTubeTranscript",
                    "parameters": [
                        {
                            "name": "url",
                            "in": "query",
                            "description": "The full URL of the YouTube video",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "start": {"type": "number"},
                                                "duration": {"type": "number"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - Invalid YouTube URL"
                        },
                        "404": {
                            "description": "Transcript not available for this video"
                        },
                        "429": {
                            "description": "Rate limit exceeded"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {}
        }
    }
    return jsonify(schema)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded", description=str(e.description)), 429

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)