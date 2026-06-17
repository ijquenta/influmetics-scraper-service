# TikTok Profile Scraper API By Apify

Thin FastAPI wrapper around Apify's [`clockworks/tiktok-scraper`](https://apify.com/clockworks/tiktok-scraper) actor. Exposes a single endpoint to scrape public TikTok profile data (profile info + videos).

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

```
APIFY_API_TOKEN=ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_KEY=<any string, used as bearer for X-API-Key header>
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

**Error codes** (from the actor, passed through in results):

| errorCode | Meaning |
|-----------|---------|
| `PROFILE_PRIVATE` | Profile is private |
| `NOT_FOUND` | Profile doesn't exist |
| `PROFILE_EMPTY` | No videos or behind login wall |

## Auth

All POST requests require `X-API-Key` header. Key is set via `API_KEY` in `.env`. No default fallback — if unset, the app crashes on startup with `RuntimeError`.

## CORS

Wide open (`*`). Tighten `allow_origins` in `main.py` if needed.

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
│   └── apify_service.py     # Apify actor client wrapper
├── requirements.txt
├── .env.example
└── .env                     # (gitignored)
```
