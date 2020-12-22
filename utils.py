from datetime import datetime
from log import logging
from sqlalchemy.orm import sessionmaker
from model.database import engine
from model.model import Playlist, Video, Statistics


def get_date(published_at):
    try:
        published_at = datetime.strptime(
            published_at, "%Y-%m-%dT%H:%M:%SZ"
        )
    except:
        published_at = datetime.strptime(
            published_at, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        pass
    return published_at

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def add_videos(yt, video_ids, playlist_id):

    Session = sessionmaker(bind=engine)
    session = Session()

    next_page_token = None
    videos = divide_chunks(video_ids, 50)
    for v in videos:
        video_ids_str = ",".join(v)
        while True:
            request = yt.videos().list(
                part="snippet,statistics", id=video_ids_str, pageToken=next_page_token
            )
            response = request.execute()

            for i in response["items"]:
                snippet = i["snippet"]
                stats = i["statistics"]
                video_id = i["id"]

                # add video if it does not exist yet
                if session.query(Video).filter_by(video_id=video_id).first() is None:
                    tags = None
                    if "tags" in snippet.keys():
                        tags = ",".join(snippet["tags"])

                    published_at = get_date(snippet["publishedAt"])

                    v = Video(
                        video_id,
                        playlist_id,
                        published_at,
                        snippet["channelId"],
                        snippet["title"],
                        snippet["description"],
                        snippet["channelTitle"],
                        tags,
                        snippet["categoryId"],
                    )
                    session.add(v)

                # add statistics
                if 'commentCount' not in stats.keys():
                    stats['commentCount'] = 0
                if 'likeCount' not in stats.keys():
                    stats['likeCount'] = 0
                if 'dislikeCount' not in stats.keys():
                    stats['dislikeCount'] = 0
                if 'viewCount' not in stats.keys():
                    stats['viewCount'] = 0

                s = Statistics(video_id, stats['viewCount'], stats['likeCount'], stats['dislikeCount'], stats['commentCount'])
                session.add(s)

            next_page_token = response.get("nextPageToken")
            if next_page_token is None:
                break
    session.commit()
    logging.warning(f"Added {len(video_ids)} to the Statistics table")


def get_playlist_videos(yt, playlist_id):
    next_page_token = None
    video_ids = []
    while True:
        request = yt.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()
        for i in response["items"]:
            video_id = i["contentDetails"]["videoId"]
            video_ids.append(video_id)
        next_page_token = response.get("nextPageToken")
        if next_page_token is None:
            break
    logging.warning(f"Retrieved {len(video_ids)} videos from playlist {playlist_id}")
    return video_ids
