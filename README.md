# Influmetics Scraper Service

FastAPI wrapper around Apify's TikTok scrapers. Scrapes profiles + comments for influencer CRM with AI-powered comment analysis.

## Stack

- Python 3.13 + FastAPI + Uvicorn
- [apify-client](https://pypi.org/project/apify-client/) v3 (async)
- Pydantic v2 for request validation

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` (see `.env.example`):

```env
APIFY_API_TOKEN=ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_KEY=<any string, used as bearer for X-API-Key header>
APIFY_TIMEOUT_SECONDS=120
CORS_ORIGINS=["*"]
```

## Run

```bash
uvicorn main:app --reload
# or
python main.py
```

Listens on `0.0.0.0:8000`.

## Endpoints

### `GET /`

Health check.

```
200 {"status":"ok","service":"tiktok-profile-scraper"}
```

### `POST /scrape/profile`

Scrape one or more TikTok profiles.

**Headers:** `X-API-Key: <your_api_key>`

**Body:**

```json
{
  "profiles": ["apifytech", "tiktok"],
  "resultsPerPage": 50
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `profiles` | `string[]` | **required** | Usernames (with or without @) |
| `resultsPerPage` | `int` | `50` | Max videos per profile (1-200) |
| `shouldDownloadVideos` | `bool` | `false` | Download video files to storage |
| `shouldDownloadCovers` | `bool` | `false` | Download cover images to storage |
| `shouldDownloadSlideshowImages` | `bool` | `false` | Download slideshow images |
| `shouldDownloadSubtitles` | `bool` | `false` | Download subtitle files |

**Response:**

```json
{
  "profiles": ["apifytech"],
  "total": 18,
  "results": [
    {
      "id": "7353646097262202145",
      "text": "video caption",
      "authorMeta": { "name": "apifytech", "fans": 852, ... },
      "videoMeta": { "duration": 59, ... },
      "diggCount": 725,
      "playCount": 83900,
      "shareCount": 30,
      "commentCount": 10,
      "hashtags": [{ "name": "fyp" }, ...],
      ...
    }
  ]
}
```

Refer to [Apify docs](https://apify.com/clockworks/tiktok-scraper/api) for full output schema.

### `POST /scrape/comments`

Scrape comments from specific TikTok video URLs.

**Headers:** `X-API-Key: <your_api_key>`

**Body:**

```json
{
  "videoUrls": ["https://www.tiktok.com/@user/video/123"],
  "commentsPerPost": 30,
  "maxRepliesPerComment": 0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `videoUrls` | `string[]` | **required** | TikTok video URLs (1-20) |
| `commentsPerPost` | `int` | `30` | Max comments per video (1-200) |
| `maxRepliesPerComment` | `int` | `0` | Max reply depth to fetch (0-10) |

**Response:**

```json
{
  "videoUrls": ["https://www.tiktok.com/@user/video/123"],
  "total": 30,
  "results": [
    {
      "text": "great video!",
      "diggCount": 42,
      "replyCommentTotal": 3,
      "createTimeISO": "2024-08-06T11:21:16.000Z",
      "uniqueId": "commenter_user",
      ...
    }
  ]
}
```

### `POST /scrape/profile-with-comments`

Combined endpoint: scrapes profile, picks the top N most-commented videos, and fetches their comments in one call. Saves credits by avoiding unnecessary comment scraping.

**Headers:** `X-API-Key: <your_api_key>`

**Body:**

```json
{
  "profiles": ["username"],
  "resultsPerPage": 50,
  "topVideos": 3,
  "commentsPerPost": 30,
  "maxRepliesPerComment": 0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `profiles` | `string[]` | **required** | Usernames (with or without @) |
| `resultsPerPage` | `int` | `50` | Max videos per profile (1-200) |
| `topVideos` | `int` | `3` | Number of most-commented videos to analyze (1-20) |
| `commentsPerPost` | `int` | `30` | Max comments per video (1-200) |
| `maxRepliesPerComment` | `int` | `0` | Max reply depth (0-10) |
| `shouldDownloadVideos` | `bool` | `false` | Download video files to storage |
| `shouldDownloadCovers` | `bool` | `false` | Download cover images to storage |
| `shouldDownloadSlideshowImages` | `bool` | `false` | Download slideshow images |
| `shouldDownloadSubtitles` | `bool` | `false` | Download subtitle files |

**Response:**

```json
{
  "profiles": ["username"],
  "total": 50,
  "results": [...],
  "comments": [...],
  "analyzedVideos": 3
}
```

**HTTP errors:**

| Status | When |
|--------|------|
| `401` | Invalid or missing `X-API-Key` |
| `422` | Invalid request body (Pydantic validation) |
| `504` | Apify actor timed out (see `APIFY_TIMEOUT_SECONDS`) |
| `500` | Unexpected server error |

**Actor error codes** (profile scraper — returned inside results array):

| errorCode | Meaning |
|-----------|---------|
| `PROFILE_PRIVATE` | Profile is private |
| `NOT_FOUND` | Profile doesn't exist |
| `PROFILE_EMPTY` | No videos or behind login wall |

**Actor error codes** (comments scraper — returned inside results array):

| errorCode | Meaning |
|-----------|---------|
| `POST_NOT_FOUND_OR_PRIVATE` | Post URL is gone or private |
| `POST_SENSITIVE` | Post is flagged as sensitive content |
| `PROFILE_PRIVATE` | Profile is private |
| `NOT_FOUND` | Profile or hashtag does not exist |

## Auth

All POST requests require `X-API-Key` header. Key is set via `API_KEY` env var. Validated on first request, not at startup.

## CORS

Controlled via `CORS_ORIGINS` env var (JSON array). Default: `["*"]` (wide open). Set to specific origins for production:

```env
CORS_ORIGINS=["https://myapp.com", "https://admin.myapp.com"]
```

## Project Structure

```
.
├── main.py                  # App entry, routes
├── core/
│   ├── __init__.py
│   └── security.py          # API key auth dependency
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic request models
├── services/
│   ├── __init__.py
│   ├── apify_service.py     # Profile scraper (clockworks/tiktok-scraper)
│   └── comments_service.py  # Comments scraper (clockworks/tiktok-comments-scraper)
├── requirements.txt
├── .env.example
└── .env                     # (gitignored)
```
