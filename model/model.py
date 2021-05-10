import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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
    comments = relationship("Comment", back_populates="video")

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

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    video_id = Column(String, ForeignKey('videos.video_id'))
    text = Column(Text)
    author = Column(String)
    like_count = Column(Integer)
    author_channel_id = Column(String)
    published_at = Column(DateTime)
    video = relationship("Video", back_populates="comments")

    def __init__(self, video_id, text, author, like_count, author_channel_id, published_at):
        self.video_id = video_id
        self.text = text
        self.author = author
        self.like_count = like_count
        self.author_channel_id = author_channel_id
        self.published_at = published_at

class CommentTerm(Base):
    __tablename__ = "comment_terms"
    id = Column(Integer, primary_key=True)
    term = Column(Text)
    frequency = Column(Integer)
    n_likes = Column(Integer)

    def __init__(self, term, frequency, n_likes):
        self.term = term
        self.frequency = frequency
        self.n_likes = n_likes

Base.metadata.create_all(bind=engine)
