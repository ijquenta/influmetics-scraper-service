import os
import asyncio
import logging
from functools import lru_cache
from apify_client import ApifyClientAsync

logger = logging.getLogger(__name__)

ACTOR_ID = "clockworks/tiktok-comments-scraper"
_TIMEOUT_SECONDS = int(os.getenv("APIFY_TIMEOUT_SECONDS", "120"))


@lru_cache
def _get_token() -> str | None:
    return os.getenv("APIFY_API_TOKEN")


@lru_cache
def _get_client() -> ApifyClientAsync:
    token = _get_token()
    if not token:
        raise RuntimeError("APIFY_API_TOKEN environment variable is not set")
    return ApifyClientAsync(token)


def build_video_url(username: str, video_id: str) -> str:
    return f"https://www.tiktok.com/@{username}/video/{video_id}"


async def scrape_comments(
    video_urls: list[str],
    comments_per_post: int = 30,
    max_replies_per_comment: int = 0,
) -> list[dict]:
    run_input = {
        "postURLs": video_urls,
        "commentsPerPost": comments_per_post,
        "maxRepliesPerComment": max_replies_per_comment,
    }

    client = _get_client()
    try:
        run = await asyncio.wait_for(
            client.actor(ACTOR_ID).call(run_input=run_input),
            timeout=_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Comments actor call timed out after %ds", _TIMEOUT_SECONDS)
        raise TimeoutError(f"Comments scraping timed out after {_TIMEOUT_SECONDS}s")

    dataset = client.dataset(run.default_dataset_id)
    return [item async for item in dataset.iterate_items()]
