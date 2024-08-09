from flask import Flask, jsonify, request, abort, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import JSONFormatter, SRTFormatter, TextFormatter
from pytube import YouTube
import os
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv


load_dotenv()

sentry_dsn = os.environ.get('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        # Disable performance monitoring
        traces_sample_rate=0.0,
        # Only send errors, not warnings or info events
        send_default_pii=False,
        before_send=lambda event, hint: event if event['level'] == 'error' else None
    )
else:
    print("Warning: SENTRY_DSN not set. Error reporting will be disabled.")

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
    storage_uri="memory://"
)

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, World!")

@app.route('/api/transcript', methods=['GET'])
@limiter.limit("10 per minute")   # add a specific rate limit for this endpoint
def get_transcript():
    youtube_url = request.args.get('url')
    output_type = request.args.get('output', 'json').lower()  # default to 'json' if not specified

    if not youtube_url:
        abort(400, description="Missing YouTube URL")
    
    if output_type not in ['json', 'srt', 'text']:
        abort(400, description="Invalid output type. Use 'json', 'srt', or 'text'.")

    try:
        yt = YouTube(youtube_url)
        video_id = yt.video_id
    except Exception as e:
        logger.error(f"Error parsing YouTube URL: {str(e)}")
        abort(400, description="Invalid YouTube URL")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        if output_type == 'json':
            formatted_transcript = JSONFormatter().format_transcript(transcript)
            content_type = 'application/json'
        elif output_type == 'srt':
            formatted_transcript = SRTFormatter().format_transcript(transcript)
            content_type = 'text/plain'
        else:  # output_type == 'text'
            formatted_transcript = TextFormatter().format_transcript(transcript)
            content_type = 'text/plain'

        logger.info(f"Successfully fetched transcript for video ID: {video_id}")
        return formatted_transcript, 200, {'Content-Type': content_type}
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
            "description": "Retrieves transcript data for YouTube videos in JSON, SRT, or plain text format.",
            "version": "v1.1.0"
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
                        },
                        {
                            "name": "output",
                            "in": "query",
                            "description": "The desired output format (json, srt, or text)",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["json", "srt", "text"],
                                "default": "json"
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
                                },
                                "text/plain": {
                                    "schema": {
                                        "type": "string",
                                        "description": "SRT or plain text formatted transcript"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - Invalid YouTube URL or output format"
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

@app.route('/privacy-policy', methods=['GET'])
def privacy_policy():
    policy = """
    <h1>Privacy Policy for YouTube Transcript API</h1>
    <p>Last updated: 28 July 2024</p>
    
    <p>This Privacy Policy describes Our policies and procedures on the collection, use and disclosure of Your information when You use the Service and tells You about Your privacy rights and how the law protects You.</p>
    
    <h2>Interpretation and Definitions</h2>
    <h3>Interpretation</h3>
    <p>The words of which the initial letter is capitalized have meanings defined under the following conditions. The following definitions shall have the same meaning regardless of whether they appear in singular or in plural.</p>
    
    <h3>Definitions</h3>
    <p>For the purposes of this Privacy Policy:</p>
    <ul>
        <li><strong>Service</strong> refers to the YouTube Transcript API.</li>
        <li><strong>You</strong> means the individual accessing or using the Service, or the company, or other legal entity on behalf of which such individual is accessing or using the Service, as applicable.</li>
    </ul>
    
    <h2>Collecting and Using Your Personal Data</h2>
    <h3>Types of Data Collected</h3>
    <p>While using Our Service, we do not collect any personal data from You.</p>
    
    <h3>Use of Your Personal Data</h3>
    <p>We do not collect or store any personal data. The Service is designed to retrieve transcripts from YouTube videos without storing any information about the requests or the users making those requests.</p>
    
    <h3>Retention of Your Personal Data</h3>
    <p>The Company does not retain any personal data.</p>
    
    <h2>Children's Privacy</h2>
    <p>Our Service does not address anyone under the age of 13. We do not knowingly collect personally identifiable information from anyone under the age of 13.</p>
    
    <h2>Changes to this Privacy Policy</h2>
    <p>We may update Our Privacy Policy from time to time. We will notify You of any changes by posting the new Privacy Policy on this page.</p>
    
    <p>We will let You know via email and/or a prominent notice on Our Service, prior to the change becoming effective and update the "Last updated" date at the top of this Privacy Policy.</p>
    
    <p>You are advised to review this Privacy Policy periodically for any changes. Changes to this Privacy Policy are effective when they are posted on this page.</p>
    
    <h2>Contact Us</h2>
    <p>If you have any questions about this Privacy Policy, You can contact us:</p>
    <ul>
        <li>By email: james [at] jamesflores.net</li>
    </ul>
    """
    return render_template_string(policy)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)