import os
import pickle
import numpy as np
from datetime import datetime

from dotenv import load_dotenv

from auth import authenticate
from log import logging
from model.database import engine
from model.model import Playlist, Video, Statistics
from utils import divide_chunks, get_playlist_videos, add_videos
from sqlalchemy.orm import sessionmaker



if __name__ == "__main__":
    load_dotenv()

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        youtube = authenticate()
        playlists = session.query(Playlist).all()
        for p in playlists:
            logging.warning(f"Analysing playlist: {p.name}")
            video_ids = get_playlist_videos(youtube, p.playlist_id)
            add_videos(youtube, video_ids, p.playlist_id)
    except Exception as e:
        logging.error(e)
