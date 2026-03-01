from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import os
import sys
from datetime import datetime, timedelta

from game_crawlers.nba.bbref_crawler import BBRefSpider, BBRefScoreboard

# Credentials and DB host read from environment variables.
# Set DB_HOST to the Docker container name or IP when running against a container.
USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]

if __name__ == "__main__":
    # Default to yesterday. Optionally pass a date as YYYY-MM-DD argument.
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
    else:
        target_date = datetime.now() - timedelta(days=1)

    print(f"Scraping games for {target_date.strftime('%Y-%m-%d')}")

    url = [BBRefScoreboard().get_urls_date(target_date)]

    settings = get_project_settings()
    settings["COOKIES_ENABLED"] = False
    settings["DOWNLOAD_DELAY"] = 3
    settings["LOG_LEVEL"] = "INFO"
    settings["ITEM_PIPELINES"] = {
        "game_crawlers.nba.pipelines.DBWriterPipeline": 100,
    }
    settings["AUTOTHROTTLE_ENABLED"] = True
    settings["AUTOTHROTTLE_TARGET_CONCURRENCY"] = 1

    process = CrawlerProcess(settings)
    process.crawl(BBRefSpider, urls=url)
    print("starting crawler")
    process.start()
    print("crawling completed")
