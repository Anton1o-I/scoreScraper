import os
from sqlalchemy import create_engine
from db import nba

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]
HOST = os.environ.get("DB_HOST", "localhost")

if __name__ == "__main__":
    engine = create_engine(
        f"postgresql://{USER}:{PASSWORD}@{HOST}:5432/nba_stats", echo=True
    )
    nba.Base.metadata.create_all(engine)
