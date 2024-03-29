import re
import pandas as pd
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm

from tqdm import tqdm
from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from model.database import engine
from model.model import Comment, Video, CommentTerm


def preprocess_text(txt):
    txt = " ".join(re.findall("[a-zA-Z]+", txt))
    return txt


def write_frequent_terms(counter, fn, ne_likes=None):
    with open(f"{fn}.csv", mode="w") as fp:
        fp.write("term,frequency,likes\n")
        for term, freq in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            if ne_likes is None:
                fp.write("{},{}\n".format(term, freq, 0))
            else:
                fp.write("{},{}\n".format(term, freq, ne_likes[term]))


if __name__ == "__main__":
    MAX_DAYS_AGO = 120

    nlp = en_core_web_sm.load()

    Session = sessionmaker(bind=engine)
    session = Session()

    comments = session.query(Comment).order_by(desc(Comment.published_at))
    video_titles = [
        preprocess_text(v.title)
        for v in session.query(Video).filter(Video.video_id).distinct()
    ]

    named_entities = []
    ne_likes = defaultdict(int)
    today = datetime.now()
    for idx, c in tqdm(enumerate(comments)):
        comment_entities = (
            []
        )  # no double entities in comments (e.g. by repeating the same artist name)
        text_processed = preprocess_text(c.text)
        text_entities = nlp(text_processed)
        for x in text_entities.ents:
            if x.text not in comment_entities:
                # print(x.text, x.label_)
                named_entities.append(x.text)
                ne_likes[x.text] += 1
                comment_entities.append(x.text)

        days_ago = (today - c.published_at).days

        if days_ago > MAX_DAYS_AGO:
            break

    
    num_deleted_items = session.query(CommentTerm).delete()
    print("Truncated {} items".format(num_deleted_items))
    session.commit()
    
    c = Counter(named_entities)
    write_frequent_terms(c, "popular_terms.csv", ne_likes=ne_likes)
