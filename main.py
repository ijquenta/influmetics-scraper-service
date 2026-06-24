import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ScrapeProfileRequest, ScrapeCommentsRequest, ProfileWithCommentsRequest
from services.apify_service import scrape_profiles, is_configured as apify_configured
from services.comments_service import scrape_comments, build_video_url
from core.security import get_api_key

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", '["*"]')
try:
    origins = json.loads(CORS_ORIGINS)
except json.JSONDecodeError:
    origins = [CORS_ORIGINS]

app = FastAPI(
    title="TikTok Profile Scraper API",
    description="Scrapes public TikTok profile data via Apify",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "influmetics service",
        "apify_configured": apify_configured(),
    }


@app.post("/scrape/profile")
async def get_profile(request: ScrapeProfileRequest, api_key: str = Depends(get_api_key)):
    try:
        data = await scrape_profiles(
            profiles=request.profiles,
            results_per_page=request.resultsPerPage,
            should_download_videos=request.shouldDownloadVideos,
            should_download_covers=request.shouldDownloadCovers,
            should_download_slideshow_images=request.shouldDownloadSlideshowImages,
            should_download_subtitles=request.shouldDownloadSubtitles,
        )
        return {"profiles": request.profiles, "total": len(data), "results": data}
    except TimeoutError as e:
        logger.error("Request timed out: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except Exception:
        logger.exception("Failed to scrape profiles %s", request.profiles)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/scrape/comments")
async def get_comments(request: ScrapeCommentsRequest, api_key: str = Depends(get_api_key)):
    try:
        data = await scrape_comments(
            video_urls=request.videoUrls,
            comments_per_post=request.commentsPerPost,
            max_replies_per_comment=request.maxRepliesPerComment,
        )
        return {"videoUrls": request.videoUrls, "total": len(data), "results": data}
    except TimeoutError as e:
        logger.error("Request timed out: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except Exception:
        logger.exception("Failed to scrape comments for %s", request.videoUrls)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/scrape/profile-with-comments")
async def get_profile_with_comments(
    request: ProfileWithCommentsRequest,
    api_key: str = Depends(get_api_key),
):
    try:
        profile_data = await scrape_profiles(
            profiles=request.profiles,
            results_per_page=request.resultsPerPage,
            should_download_videos=request.shouldDownloadVideos,
            should_download_covers=request.shouldDownloadCovers,
            should_download_slideshow_images=request.shouldDownloadSlideshowImages,
            should_download_subtitles=request.shouldDownloadSubtitles,
        )

        videos_with_comments = [
            v for v in profile_data
            if v.get("authorMeta") and v.get("id") and v.get("commentCount", 0) > 0
        ]
        videos_with_comments.sort(key=lambda v: v["commentCount"], reverse=True)
        top_videos = videos_with_comments[:request.topVideos]

        video_urls = [
            build_video_url(v["authorMeta"]["name"], v["id"])
            for v in top_videos
        ]

        comments = []
        if video_urls:
            comments = await scrape_comments(
                video_urls=video_urls,
                comments_per_post=request.commentsPerPost,
                max_replies_per_comment=request.maxRepliesPerComment,
            )

        return {
            "profiles": request.profiles,
            "total": len(profile_data),
            "results": profile_data,
            "comments": comments,
            "analyzedVideos": len(video_urls),
        }
    except TimeoutError as e:
        logger.error("Request timed out: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except Exception:
        logger.exception("Failed to scrape profile with comments for %s", request.profiles)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
