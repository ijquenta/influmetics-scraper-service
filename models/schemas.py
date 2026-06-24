from pydantic import BaseModel, Field


class ScrapeProfileRequest(BaseModel):
    profiles: list[str] = Field(..., min_length=1, max_length=100)
    resultsPerPage: int = Field(default=50, ge=1, le=200)
    shouldDownloadVideos: bool = False
    shouldDownloadCovers: bool = False
    shouldDownloadSlideshowImages: bool = False
    shouldDownloadSubtitles: bool = False


class ScrapeCommentsRequest(BaseModel):
    videoUrls: list[str] = Field(..., min_length=1, max_length=20)
    commentsPerPost: int = Field(default=30, ge=1, le=200)
    maxRepliesPerComment: int = Field(default=0, ge=0, le=10)


class ProfileWithCommentsRequest(BaseModel):
    profiles: list[str] = Field(..., min_length=1, max_length=100)
    resultsPerPage: int = Field(default=50, ge=1, le=200)
    commentsPerPost: int = Field(default=30, ge=1, le=200)
    maxRepliesPerComment: int = Field(default=0, ge=0, le=10)
    topVideos: int = Field(default=3, ge=1, le=20)
    shouldDownloadVideos: bool = False
    shouldDownloadCovers: bool = False
    shouldDownloadSlideshowImages: bool = False
    shouldDownloadSubtitles: bool = False
