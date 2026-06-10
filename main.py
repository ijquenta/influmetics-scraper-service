import logging
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ScrapeProfileRequest
from services.apify_service import scrape_profiles
from core.security import get_api_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TikTok Profile Scraper API",
    description="Scrapes public TikTok profile data via Apify",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "tiktok-profile-scraper"}


@app.post("/scrape/profile")
async def get_profile(request: ScrapeProfileRequest, api_key: str = Depends(get_api_key)):
    try:
        data = await scrape_profiles(request.profiles, request.resultsPerPage)
        return {"profiles": request.profiles, "total": len(data), "results": data}
    except Exception:
        logger.exception("Failed to scrape profiles %s", request.profiles)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
