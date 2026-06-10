from pydantic import BaseModel, Field

class ScrapeProfileRequest(BaseModel):
    profiles: list[str] = Field(..., min_length=1, max_length=100)
    resultsPerPage: int = Field(default=50, ge=1, le=200)
    shouldDownloadVideos: bool = False
    shouldDownloadCovers: bool = False
    shouldDownloadSlideshowImages: bool = False
    shouldDownloadSubtitles: bool = False
