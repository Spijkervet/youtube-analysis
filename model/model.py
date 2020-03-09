import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .database import engine


Base = declarative_base()

class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(String, unique=True)
    name = Column(String)
    genre = Column(String)

    def __init__(self, playlist_id, name, genre):
        self.playlist_id = playlist_id
        self.name = name
        self.genre = genre

        
class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    video_id = Column(String, unique=True)
    playlist_id = Column(String)
    published_at = Column(DateTime)
    channel_id = Column(String)
    title = Column(String)
    description = Column(String)
    channel_title = Column(String)
    tags = Column(String)
    category_id = Column(Integer)

    def __init__(self, video_id, playlist_id, published_at, channel_id, title, description, channel_title, tags, category_id): #, views, likes, dislikes, comment_count):
        self.video_id = video_id
        self.playlist_id = playlist_id
        self.published_at = published_at
        self.channel_id = channel_id
        self.title = title
        self.description = description
        self.channel_title = channel_title
        self.tags = tags
        self.category_id = category_id

        # self.snippet = snippet
        # self.views = views
        # self.likes = likes
        # self.dislikes = dislikes
        # self.comment_count = comment_count

    def __repr__(self):
        return f'{self.id}'


class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    video_id = Column(String, ForeignKey('videos.video_id'))
    datetime = Column('datetime', DateTime)
    views = Column(Integer)
    likes = Column(Integer)
    dislikes = Column(Integer)
    comment_count = Column(Integer)

    def __init__(self, video_id, views, likes, dislikes, comment_count):
        self.video_id = video_id
        self.datetime = datetime.datetime.now()
        self.views = views
        self.likes = likes
        self.dislikes = dislikes
        self.comment_count = comment_count

Base.metadata.create_all(bind=engine)
