import os
import pickle
import numpy as np
from datetime import datetime

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

from model.database import engine
from model.model import Playlist, Video, Statistics
from utils import divide_chunks
from sqlalchemy.orm import sessionmaker

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

import logging
import logging.handlers

load_dotenv()

smtp_creds = (os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
smtp_handler = logging.handlers.SMTPHandler(mailhost=("smtp.gmail.com", 587),
                                            fromaddr=os.getenv("SMTP_USER"), 
                                            toaddrs=[os.getenv("SMTP_USER")],
                                            subject="Error in YouTube Analysis",
                                            credentials=smtp_creds,
                                            secure=())
smtp_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(),
        smtp_handler
    ]
)

Session = sessionmaker(bind=engine)
session = Session()


def authenticate():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)


    if os.path.exists('credentials.p'):
        credentials = pickle.load(open('credentials.p', 'rb'))
    else:
        credentials = flow.run_console()
        pickle.dump(credentials, open('credentials.p', 'wb'))
    
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials, cache_discovery=False)
    return youtube


def get_playlist_videos(yt, playlist_id):
    next_page_token = None
    video_ids = []
    while True:
        request = yt.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for i in response['items']:
            video_id = i['contentDetails']['videoId']
            video_ids.append(video_id)
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break
    logging.warning(f"Retrieved {len(video_ids)} videos from playlist {playlist_id}")
    return video_ids

def get_video_statistics(yt, video_ids, playlist_id):
    next_page_token = None
    videos = divide_chunks(video_ids, 50)
    for v in videos:
        video_ids_str = ','.join(v)
        while True:
            request = yt.videos().list(
                part="snippet,statistics",
                id=video_ids_str,
                pageToken=next_page_token
            )
            response = request.execute()

            for i in response['items']:
                snippet = i['snippet']
                stats = i['statistics']
                video_id = i['id']

                # add video if it does not exist yet
                if(session.query(Video).filter_by(video_id=video_id).first() is None):
                    tags = None
                    if 'tags' in snippet.keys():
                        tags = ','.join(snippet['tags'])

                    published_at = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    v = Video(video_id, playlist_id, published_at, snippet['channelId'], snippet['title'], snippet['description'], snippet['channelTitle'],
                        tags, snippet['categoryId'])
                    session.add(v)
                    session.commit()

                # add statistics
                if 'commentCount' not in stats.keys():
                    stats['commentCount'] = 0
                if 'likeCount' not in stats.keys():
                    stats['likeCount'] = 0
                if 'dislikeCount' not in stats.keys():
                    stats['dislikeCount'] = 0

                s = Statistics(video_id, stats['viewCount'], stats['likeCount'], stats['dislikeCount'], stats['commentCount'])
                session.add(s)
                session.commit()

            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    
    logging.warning(f"Added {len(video_ids)} to the Statistics table")

if __name__ == "__main__":
    try:
        asfasdf
        youtube = authenticate()
        playlists = session.query(Playlist).all()
        for p in playlists:
            logging.warning(f"Analysing playlist: {p.name}")
            video_ids = get_playlist_videos(youtube, p.playlist_id)
            get_video_statistics(youtube, video_ids, p.playlist_id)
    except Exception as e:
        logging.error(e)