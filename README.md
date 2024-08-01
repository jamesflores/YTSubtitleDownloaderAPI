# YouTube Transcript API

## Overview
This Flask application provides an API to fetch transcripts from YouTube videos. It was created to allow it for use as an action in custom GPTs.

## Features
- Fetches transcripts from YouTube videos using the video URL
- Supports JSON, SRT, and plain text output formats
- Offers an optimization option to reduce transcript size
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

Send a GET request to `/api/transcript` with a `url` query parameter containing the YouTube video URL. You can also specify the output format using the `output` parameter and enable optimization with the `optimize` parameter.

### Parameters

- `url` (required): The YouTube video URL
- `output` (optional): The output format. Can be 'json' (default), 'srt', or 'text'
- `optimize` (optional): Set to 'true' to enable transcript optimization

### JSON Output (Default)

```
GET /api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

#### Response Format (JSON)

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

### SRT Output

To get the transcript in SRT format, use the `output=srt` parameter:

```
GET /api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&output=srt
```

#### Response Format (SRT)

The API returns the transcript in SubRip Subtitle (SRT) format, which is widely used for subtitles. The response will be plain text with the following structure:

```
1
00:00:43,360 --> 00:00:49,719
Going To Give You Up never going to let

2
00:00:46,199 --> 00:00:53,640
you down never going to run around and

3
00:00:49,719 --> 00:00:56,120
desert you never going to make you cry

// ... more subtitle entries
```

This format is compatible with most video players and subtitle editors.

### Plain Text Output

To get the transcript in plain text format, use the `output=text` parameter:

```
GET /api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&output=text
```

#### Response Format (Text)

The API returns the transcript as plain text, with each line representing a segment of the transcript:

```
Going To Give You Up never going to let
you down never going to run around and
desert you never going to make you cry
// ... more lines
```

### Optimization

To optimize the transcript and reduce its size, add the `optimize=true` parameter:

```
GET /api/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&optimize=true
```

This option removes repetitive elements and combines consecutive entries, resulting in a more compact transcript.

## Rate Limiting
The API implements rate limiting to ensure fair usage:
- 10 requests per minute per IP address for all endpoints

## Privacy
This application does not store any personal data. For more details, see the `/privacy-policy` endpoint.

## Custom GPT Integration
I wrote this API to use it in my custom GPT "Church Service Timestamp Generator". This GPT can analyze church service videos and generate timestamped outlines. You can access it here: [Church Service Timestamp Generator](https://chatgpt.com/g/g-sv1MkzVrI-church-service-timestamp-generator)

## License
This project is licensed under the MIT License.

## Contact
james@jamesflores.net