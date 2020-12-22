import csv
from sqlalchemy.orm import sessionmaker
from model.database import engine
from model.model import Playlist

Session = sessionmaker(bind=engine)
session = Session()

with open('playlists.csv', 'r') as f:
    r = csv.reader(f, delimiter=',')
    next(r) # skip header
    for row in r:
        url, name, genre = row
        playlist_id = url.replace('https://www.youtube.com/playlist?list=', '')

        if session.query(Playlist).filter_by(playlist_id=playlist_id).first() is None:
            playlist = Playlist(playlist_id, name, genre)
            session.add(playlist)
            session.commit()
