from sqlalchemy import create_engine
engine = create_engine('sqlite:///database.sqlite', echo=False)
connection = engine.connect()

