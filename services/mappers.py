def map_video_item(raw: dict) -> dict:
    author = raw.get("authorMeta", {})
    video = raw.get("videoMeta", {})

    hashtags = [h.get("name", "") for h in raw.get("hashtags", []) if h.get("name")]

    return {
        "id": raw.get("id"),
        "text": raw.get("text"),
        "createTimeISO": raw.get("createTimeISO"),
        "webVideoUrl": raw.get("webVideoUrl"),
        "diggCount": raw.get("diggCount", 0),
        "playCount": raw.get("playCount", 0),
        "shareCount": raw.get("shareCount", 0),
        "commentCount": raw.get("commentCount", 0),
        "collectCount": raw.get("collectCount", 0),
        "repostCount": raw.get("repostCount", 0),
        "hashtags": hashtags,
        "isSponsored": raw.get("isSponsored", False),
        "isPinned": raw.get("isPinned", False),
        "mentions": raw.get("mentions", []),
        "textLanguage": raw.get("textLanguage"),
        "author": {
            "id": author.get("id"),
            "name": author.get("name"),
            "nickName": author.get("nickName"),
            "profileUrl": author.get("profileUrl"),
            "avatar": author.get("avatar"),
            "verified": author.get("verified", False),
            "signature": author.get("signature"),
            "fans": author.get("fans", 0),
            "heart": author.get("heart", 0),
            "video": author.get("video", 0),
            "following": author.get("following", 0),
            "friends": author.get("friends", 0),
            "privateAccount": author.get("privateAccount", False),
        },
        "video": {
            "duration": video.get("duration", 0),
            "coverUrl": video.get("coverUrl"),
        },
    }


def _extract_video_id(video_url: str | None) -> str | None:
    if not video_url or "/video/" not in video_url:
        return None
    return video_url.split("/video/")[-1].split("?")[0]


def map_comment_item(raw: dict) -> dict:
    return {
        "videoId": _extract_video_id(raw.get("videoWebUrl")),
        "text": raw.get("text"),
        "diggCount": raw.get("diggCount", 0),
        "replyCommentTotal": raw.get("replyCommentTotal", 0),
        "createTimeISO": raw.get("createTimeISO"),
        "uniqueId": raw.get("uniqueId"),
        "uid": raw.get("uid"),
    }
