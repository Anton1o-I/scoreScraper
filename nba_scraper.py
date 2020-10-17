from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import List

from game_crawlers.nba.bbref_crawler import BBRefSpider, BBRefScoreboard
from game_crawlers.nba.seasons import Seasons
from db import nba

# TODO read game ids by date in docker volume
# TODO add flags to specify date range

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]


def get_espn_ids():
    fp = "/c/Users/ainig/Desktop/gameid_data/game_ids"
    files = os.listdir(fp)

    ids = []
    for f in files:
        file_path = os.path.join(fp, f)
        if os.path.isfile(file_path):
            with open(os.path.join(fp, f)) as js:
                ids.extend(json.load(js))
    return ids


if __name__ == "__main__":
    print("getting game ids")

    settings = get_project_settings()
    settings["COOKIES_ENABLED"] = False
    settings["DOWNLOAD_DELAY"] = 1
    settings["LOG_LEVEL"] = "INFO"
    settings["ITEM_PIPELINES"] = {
        "game_crawlers.nba.pipelines.JsonWriterPipeline": 100,
        "game_crawlers.nba.pipelines.DBWriterPipeline": 100,
    }
    settings["AUTOTHROTTLE_ENABLED"] = True
    settings["AUTHROTTLE_TARGET_CONCURRENCY"] = 3

    url = BBRefScoreboard().get_all_scoreboard_urls()
    process = CrawlerProcess(settings)
    process.crawl(BBRefSpider, urls=url)
    print("starting crawler")
    process.start()
    print("crawling completed")
