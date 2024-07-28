# YouTube Transcript API

## Overview
This Flask application provides an API to fetch transcripts from YouTube videos. It was created to support the custom GPT "Church Service Timestamp Generator" available at [https://chatgpt.com/g/g-sv1MkzVrI-church-service-timestamp-generator](https://chatgpt.com/g/g-sv1MkzVrI-church-service-timestamp-generator).

## Features
- Fetches transcripts from YouTube videos using the video URL
- Implements rate limiting to prevent abuse
- Provides a simple privacy policy
- Offers an OpenAPI schema for easy integration

## Endpoints
- `/api/transcript`: GET request to fetch a transcript given a YouTube URL
- `/privacy-policy`: GET request to view the privacy policy
- `/openapi.json`: GET request to retrieve the OpenAPI schema

## Setup
1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the Flask app:
   ```
   flask run
   ```

## Usage

Send a GET request to `/api/transcript` with a `url` query parameter containing the YouTube video URL. For example:

```
GET /api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Response Format

The API returns a JSON array of transcript segments. Each segment is an object containing the following fields:

- `text`: The transcribed text for this segment
- `start`: The start time of the segment in seconds
- `duration`: The duration of the segment in seconds

Example response:

```json
[
    {
        "text": "Going To Give You Up never going to let",
        "start": 43.36,
        "duration": 6.359
    },
    {
        "text": "you down never going to run around and",
        "start": 46.199,
        "duration": 7.441
    },
    {
        "text": "desert you never going to make you cry",
        "start": 49.719,
        "duration": 6.401
    },
    // ... more segments
]
```

This format allows for easy parsing and use of the transcript data, including the ability to reconstruct the timing of the full transcript.

## Rate Limiting
The API implements rate limiting to ensure fair usage:
- 10 requests per minute for the `/api/transcript` endpoint

## Privacy
This application does not store any personal data. For more details, see the `/privacy-policy` endpoint.

## Custom GPT Integration
I wrote this API to use it in my custom GPT "Church Service Timestamp Generator". This GPT can analyse church service videos and generate timestamped outlines. You can access it here: [Church Service Timestamp Generator](https://chatgpt.com/g/g-sv1MkzVrI-church-service-timestamp-generator)

## License
This project is licensed under the MIT License.

## Contact
james@jamesflores.net