### Resources for scraping box score statistics

### Crawler Status

* NBA
    - ESPN - being depracated due to ESPN have inconsistencies in the html code for teams that no longer exist
    - BasketballReference - currently in development
* NFL
    - FootballReference - TODO - plans to build this crawler in the future
* MLP
    - BaseballReference - TODO - plans to build this crawler in the future

#### Selinium Driver
In order to get the game_ids for NBA games to provide those vlaues to the scoreScraper, we need to utilize a Selenium driver. This is accomplished by building the Docker image provided in the repository then exec-ing into the docker image. While in the docker image, you will need to run the start.sh file from bash in order for the settings to be correct for the driver to actually work. From there, you can run the script found in game_ids.py to pull the game ids. This information will be downloaded to a 'game_ids.json'  file in the Docker image.