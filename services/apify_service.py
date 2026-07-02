import os
import asyncio
import logging
from functools import lru_cache
from apify_client import ApifyClientAsync

logger = logging.getLogger(__name__)

ACTOR_ID = "clockworks/tiktok-scraper"
_TIMEOUT_SECONDS = int(os.getenv("APIFY_TIMEOUT_SECONDS", "120"))


@lru_cache
def _get_token() -> str | None:
    return os.getenv("APIFY_API_TOKEN")


def is_configured() -> bool:
    return bool(_get_token())


@lru_cache
def _get_client() -> ApifyClientAsync:
    token = _get_token()
    if not token:
        raise RuntimeError("APIFY_API_TOKEN environment variable is not set")
    return ApifyClientAsync(token)


async def scrape_profiles(
    profiles: list[str],
    results_per_page: int = 50,
    should_download_videos: bool = False,
    should_download_covers: bool = False,
    should_download_slideshow_images: bool = False,
    should_download_subtitles: bool = False,
) -> list[dict]:
    run_input = {
        "profiles": profiles,
        "resultsPerPage": results_per_page,
        "shouldDownloadVideos": should_download_videos,
        "shouldDownloadCovers": should_download_covers,
        "shouldDownloadSlideshowImages": should_download_slideshow_images,
        "shouldDownloadSubtitles": should_download_subtitles,
    }

    client = _get_client()
    try:
        run = await asyncio.wait_for(
            client.actor(ACTOR_ID).call(run_input=run_input),
            timeout=_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Apify actor call timed out after %ds", _TIMEOUT_SECONDS)
        raise TimeoutError(f"Scraping timed out after {_TIMEOUT_SECONDS}s")

    dataset = client.dataset(run.default_dataset_id)
    return [item async for item in dataset.iterate_items()]


HASHTAG_ACTOR_ID = "clockworks/tiktok-hashtag-scraper"


async def scrape_by_hashtags(
    hashtags: list[str] | None = None,
    keywords: list[str] | None = None,
    max_items: int = 50,
) -> list[dict]:
    clean_hashtags = [h.lstrip("#") for h in (hashtags or [])]

    run_input: dict = {
        "hashtags": clean_hashtags,
        "resultsPerPage": min(max_items, 200),
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadSubtitles": False,
    }

    if keywords:
        run_input["searchQueries"] = keywords

    client = _get_client()
    try:
        run = await asyncio.wait_for(
            client.actor(HASHTAG_ACTOR_ID).call(run_input=run_input),
            timeout=_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Hashtag scraping timed out after %ds", _TIMEOUT_SECONDS)
        raise TimeoutError(f"Hashtag scraping timed out after {_TIMEOUT_SECONDS}s")

    dataset = client.dataset(run.default_dataset_id)
    return [item async for item in dataset.iterate_items()]
