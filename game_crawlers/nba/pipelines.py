import json
import scrapy
from db import nba
import os

# TODO add SQL Pipeline instead

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]


class DBWriterPipeline(object):
    def open_spider(self, spider):
        self.db = nba.nbaDB(USER, PASSWORD)

    def close_spider(self, spider):
        self.db.session.commit()
        self.db.session.close()

    def process_item(self, item, spider):
        gid = item.get("game_data").get("game_id")
        self.db.add_record(item)
        self.db.session.commit()
        return f"game{gid} processed"


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
