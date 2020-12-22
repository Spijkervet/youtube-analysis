import pandas as pd
from sqlalchemy.orm import sessionmaker
from model.database import engine
from model.model import Comment, Video

from tqdm import tqdm

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()
    
    comments = session.query(Comment).all()
    l = []
    for c in tqdm(comments):
        video_title = c.video.title

        l.append([
            video_title,
            c.text,
            c.author,
            c.like_count,
            c.author_channel_id,
            c.published_at
        ])
    
    df = pd.DataFrame(l, columns=['video_title', 'comment', 'author', 'like_count', 'author_channel_id', 'published_at'])
    df.to_csv("comments.csv", index=False)