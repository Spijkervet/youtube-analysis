from dotenv import load_dotenv

from auth import authenticate
from sqlalchemy.orm import sessionmaker
from model.database import engine
from model.model import Video, Comment
from log import logging
from utils import divide_chunks, get_playlist_videos, add_videos, get_date


def get_comment_from_snippet(snippet, video_id):
    author = snippet["authorDisplayName"]
    text = snippet["textDisplay"]
    like_count = snippet["likeCount"]

    if "authorChannelId" in snippet.keys():
        author_channel_id = snippet["authorChannelId"]["value"]
    else:
        author_channel_id = None

    published_at = snippet["publishedAt"]

    published_at = get_date(snippet["publishedAt"])
    comment = Comment(
        video_id=video_id,
        text=text,
        author=author,
        like_count=like_count,
        author_channel_id=author_channel_id,
        published_at=published_at,
    )
    return comment

def add_comments(yt, video_ids):
    print("Analysing videos:", len(video_ids))

    Session = sessionmaker(bind=engine)
    session = Session()

    next_page_token = None
    for video_id in video_ids:
        try:
            while True:
                request = yt.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    pageToken=next_page_token,
                    maxResults=100,
                    textFormat="plainText",
                )
                response = request.execute()
                for item in response["items"]:
                    comment = item["snippet"]["topLevelComment"]

                    snippet = comment["snippet"]
                    comment = get_comment_from_snippet(snippet, video_id)
                    session.add(comment)

                    if "replies" in item.keys():
                        for reply in item["replies"]["comments"]:
                            snippet = reply["snippet"]
                            comment = get_comment_from_snippet(snippet, video_id)
                            session.add(comment)

                session.commit()
                next_page_token = response.get("nextPageToken")
                if next_page_token is None:
                    break
        except Exception as e:
            logging.error(e)
            pass

    session.commit()
    logging.warning(f"Analysed {len(video_ids)} for comments")


if __name__ == "__main__":
    load_dotenv()

    Session = sessionmaker(bind=engine)
    session = Session()

    without_music_playlist_id = "PLCWrO9OZ_XGPln0Bg-hbGi5uvbqS9rSVQ"
    try:
        yt = authenticate()
        video_ids = get_playlist_videos(yt, playlist_id=without_music_playlist_id)

        existing_video_ids = [
            v.video_id
            for v in session.query(Video).filter(Video.video_id.in_(video_ids)).all()
        ]

        new_video_ids = list(set(video_ids) - set(existing_video_ids))
        add_videos(yt, new_video_ids, without_music_playlist_id)
        add_comments(yt, new_video_ids)

    except Exception as e:
        logging.error(e)
