import os
import logging
from apify_client import ApifyClientAsync

logger = logging.getLogger(__name__)

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    raise RuntimeError("APIFY_API_TOKEN environment variable is not set")

client = ApifyClientAsync(APIFY_API_TOKEN)

ACTOR_ID = "clockworks/tiktok-scraper"

async def scrape_profiles(profiles: list[str], results_per_page: int = 5) -> list[dict]:
    run_input = {
        "profiles": profiles,
        "resultsPerPage": results_per_page,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadSubtitles": False,
    }

    run = await client.actor(ACTOR_ID).call(run_input=run_input)
    dataset = client.dataset(run.default_dataset_id)

    return [item async for item in dataset.iterate_items()]
