from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import List, Dict
import re
from datetime import datetime, timedelta

from game_crawlers.nba.seasons import Seasons
from game_crawlers.nba.fields import (
    Game,
    Record,
    Line,
    Team,
    Player,
    PlayerStats,
    TeamStats,
)


class BBRefScoreboard:
    """
    Class to pull list of dates that NBA games were played using range for regular and post season
    schedules. Some games may still be empty, but get_scoreboard_urls() will return the urls for
    all days where a game possibly occurred.
    """

    def __init__(self):
        pass

    def get_all_scoreboard_urls(self):
        url_list = list()
        for _, v in Seasons.season_info.items():
            url_list = url_list + list(
                self._get_bbref_url(v["regular_season_start"], v["regular_season_end"])
            )
            url_list = url_list + list(
                self._get_bbref_url(v["post_season_start"], v["post_season_end"])
            )
        return url_list

    def get_urls_by_range(self, start, end):
        delta = (end + timedelta(days=1) - start).days
        return [self.get_urls_date(d) for d in delta]

    def get_urls_date(self, date: datetime):
        return f"https://www.basketball-reference.com/boxscores/?month={date.month}&day={date.day}&year={date.year}"

    def _get_bbref_url(self, start, end):
        for d in self._get_dates(start, end):
            yield f"https://www.basketball-reference.com/boxscores/?month={d.month}&day={d.day}&year={d.year}"

    @staticmethod
    def _get_dates(start: datetime, end: datetime) -> List[datetime]:
        d = (end + timedelta(days=1) - start).days
        return [start + timedelta(days=i) for i in range(d)]


class BBRefSpider(Spider):
    """
    Scrapy Spider that handles all logic for parsing the scoreboard page and then the boxscore
    for basketball-reference website games.
    """

    name = "nba_boxscores"
    base_url = "https://www.basketball-reference.com"

    def __init__(self, urls: List[str], *args, **kwargs):
        super(BBRefSpider, self).__init__(*args, **kwargs)
        self.urls = urls

    def start_requests(self):
        for l in self.urls:
            yield Request(
                url=l,
                callback=self.parse_scoreboard,
            )

    def parse_scoreboard(self, response):
        games = response.xpath('//p[@class="links"]/a/@href').extract()
        for g in games:
            if re.search(r"boxscores/[0-9]", g):
                game_id = re.search(r"boxscores/([0-9A-Z]*).html", g).group(1)
                yield Request(
                    url=self.base_url + g,
                    callback=self.parse_boxscore,
                    cb_kwargs=dict(game_id=game_id),
                )

    def parse_boxscore(self, response, game_id):
        game = self.get_game_information(response, game_id)
        team_stats = self.get_team_stats(response, game_id)
        player_stats = self.get_player_stats(response, game_id)
        return {
            "game_data": game,
            "team_stats": team_stats,
            "player_stats": player_stats,
        }

    def get_game_information(self, response, game_id):
        date_str = response.xpath('//div[@class="scorebox_meta"]').re_first(
            r"[0-9]{1,2}:[0-9]{2}.*[0-9]{4}"
        )

        records = response.xpath('//div[@class="scorebox"]/div/div').re(
            r"[0-9]{1,2}-[0-9]{1,2}"
        )
        scores = response.xpath('//div[@class="scorebox"]/div/div[@class="scores"]').re(
            "[0-9]{2,3}"
        )

        ar, hr = self.get_away_home_records(records, scores)

        return dict(
            Game(
                game_id=game_id,
                date=date_str,
                home_record=dict(hr),
                away_record=dict(ar),
            )
        )

    def get_team_stats(self, response, game_id: str):
        # team_information contains len = 2 list of strings with team name information
        team_information = response.xpath("//strong/a[@itemprop='name']").getall()

        # regex parses <a href="/teams/POR/2006.html" itemprop="name">Portland Trail Blazers</a> into groups
        # POR -> "abbr", Portland Trail Blazers -> "name"
        away = re.search(
            r"teams/(?P<abbr>[A-Z]{3}).*>(?P<name>[A-Za-z0-9 ]+)<", team_information[0]
        )
        home = re.search(
            r"teams/(?P<abbr>[A-Z]{3}).*>(?P<name>[A-Za-z0-9 ]+)<", team_information[1]
        )

        away_team = Team(name=away.group("name"), abbreviation=away.group("abbr"))
        home_team = Team(name=home.group("name"), abbreviation=home.group("abbr"))

        away_stats = self.parse_team_stats(response, away.group("abbr"))
        home_stats = self.parse_team_stats(response, home.group("abbr"))

        away_stat_obj = TeamStats(
            team=dict(away_team), game_id=game_id, home=False, **away_stats
        )
        home_stat_obj = TeamStats(
            team=dict(home_team), game_id=game_id, home=True, **home_stats
        )
        return {"home_stats": dict(home_stat_obj), "away_stats": dict(away_stat_obj)}

    def get_player_stats(self, response, game_id):
        # team_information contains len = 2 list of strings with team name information
        team_information = response.xpath("//strong/a[@itemprop='name']").getall()

        # regex parses <a href="/teams/POR/2006.html" itemprop="name">Portland Trail Blazers</a> into groups
        # POR -> "abbr", Portland Trail Blazers -> "name"
        away = re.search(
            r"teams/(?P<abbr>[A-Z]{3}).*>(?P<name>[A-Za-z0-9 ]+)<", team_information[0]
        ).group("abbr")
        home = re.search(
            r"teams/(?P<abbr>[A-Z]{3}).*>(?P<name>[A-Za-z0-9 ]+)<", team_information[1]
        ).group("abbr")

        home_stats = self.parse_player_stats(response, home)
        away_stats = self.parse_player_stats(response, away)

        return {"home_stats": home_stats, "away_stats": away_stats}

    def parse_player_stats(self, response, team_abbr: str):
        # xpath is dynamically named after the teams abbreviation, so that needs to get passed into the
        # function so that we can accurately pull statistics. Player stats are found in body of table
        # and xpath will return a list of stats to parse.
        basic_xpath_str = (
            '//table[@id="box-'
            + team_abbr
            + '-game-basic"]//tbody/tr[not(@class="thead")]'
        )
        advanced_xpath_str = (
            '//table[@id="box-'
            + team_abbr
            + '-game-advanced"]//tbody/tr[not(@class="thead")]'
        )

        # Below regex returns list of html for each player on the away or home team:
        #    '<tr><th scope="row" class="left " data-append-csv="harklma01" data-stat="player" csk="Harkless,Maurice">
        #    <a href="/players/h/harklma01.html">Maurice Harkless</a></th><td class="right " data-stat="mp"
        #    csk="2453">40:53</td><td class="right " data-stat="fg">6</td><td class="right " data-stat="fga">13</td>
        #    <td class="right " data-stat="fg_pct">.462</td><td class="right iz" data-stat="fg3">0</td><td class="right "
        #    data-stat="fg3a">4</td><td class="right " data-stat="fg3_pct">.000</td><td class="right " data-stat="ft">2
        #    </td><td class="right " data-stat="fta">3</td><td class="right " data-stat="ft_pct">.667</td><td class="right
        #     " data-stat="orb">1</td><td class="right " data-stat="drb">5</td><td class="right " data-stat="trb">6</td>
        #    <td class="right " data-stat="ast">6</td><td class="right " data-stat="stl">1</td><td class="right iz" data-stat="blk">0</td><td class="right "
        #    data-stat="tov">1</td><td class="right " data-stat="pf">3</td><td class="right " data-stat="pts">14</td>
        #    <td class="right " data-stat="plus_minus">+10</td></tr>'

        basic_list = response.xpath(basic_xpath_str).getall()
        advanced_list = response.xpath(advanced_xpath_str).getall()

        basic_stats = self.parse_basic_player(basic_list)
        advanced_stats = self.parse_advanced_player(advanced_list)

        player_stats = list()
        for p in basic_stats.keys():
            combined = {**basic_stats[p], **advanced_stats[p]}
            player = PlayerStats(**combined)
            player_stats.append(dict(player))
        return player_stats

    def parse_basic_player(self, stat_list):
        bbref_to_pstat_map_basic = {
            "fg": "fgm",
            "fga": "fga",
            "fg_pct": "fg_per",
            "fg3": "x3pm",
            "fg3a": "x3pa",
            "fg3_pct": "x3p_per",
            "ft": "ftm",
            "fta": "fta",
            "ft_pct": "ft_per",
            "orb": "orebs",
            "drb": "drebs",
            "trb": "rebounds",
            "ast": "assists",
            "stl": "steals",
            "blk": "blocks",
            "tov": "turnovers",
            "pf": "fouls",
            "pts": "points",
            "plus_minus": "plus_minus",
        }
        re_player_info = r'data-append-csv="(?P<id>[a-z0-9]+)".+csk="(?P<name>.+)"><a'

        # mp -> minutes played has an extra identifying field 'csk' within the <> so it needs to be pulled with
        # it's own regex code.
        re_mp = r"data-stat=\"mp\".+>(?P<val>[0-9]{2}:[0-9]{2})</td>"
        re_stats = r"data-stat=\"(?P<stat>[a-z0-9_]+)\">(?P<val>[0-9.:+-]+)</td>"

        player_stats = dict()
        for line in stat_list:
            # this splits off the table header information for each row, which contains all of the player
            # information, name and id. The stat group contains the <tr> sections that correspond to each
            # players basic statistics
            split_header = line.split("</th>")
            name_group = split_header[0]
            stat_group = split_header[1]

            player_info = re.search(re_player_info, name_group)
            # Basketball Reference uses LastName, FirstName formatting for players
            player_name = player_info.group("name").split(",")
            player_obj = Player(
                player_id=player_info.group("id"),
                last_name=player_name[0],
                first_name=player_name[1],
            )

            s = re.search(re_mp, stat_group)
            if s is not None:
                mp = s.group("val")
            else:
                mp = "00:00"
            stat_dict = {
                "player": dict(player_obj),
                "min": self.time_string_to_hours(mp),
            }
            parsed_stats = re.findall(re_stats, stat_group)
            for s in parsed_stats:
                if s[0] in bbref_to_pstat_map_basic.keys():
                    stat_dict[bbref_to_pstat_map_basic[s[0]]] = s[1]

            # sets the default values for any missing stats
            for _, v in bbref_to_pstat_map_basic.items():
                if stat_dict.get(v, None) is None:
                    stat_dict[v] = 0
            player_stats[player_info.group("id")] = stat_dict
        return player_stats

    def parse_advanced_player(self, stat_list):
        bbref_to_pstat_map_advanced = {
            "ts_pct": "ts_per",
            "efg_pct": "efg_per",
            "fg3a_per_fga_pct": "x3p_ar",
            "fta_per_fga_pct": "ft_ar",
            "orb_pct": "oreb_per",
            "drb_pct": "dreb_per",
            "trb_pct": "reb_per",
            "ast_pct": "ast_per",
            "stl_pct": "stl_per",
            "blk_pct": "blk_per",
            "tov_pct": "tov_per",
            "usg_pct": "usg_per",
            "off_rtg": "off_rating",
            "def_rtg": "def_rating",
            "bpm": "bpm",
            "obpm": "obpm",
            "dbpm": "dbpm",
            "vorp": "vorp",
        }
        re_player_info = r'data-append-csv="(?P<id>[a-z0-9]+)".+csk="(?P<name>.+)"><a'
        re_stats = r"data-stat=\"(?P<stat>[a-z0-9_]+)\">(?P<val>[0-9.:+]+)</td>"

        # bpm field has extra information, so below regex parses all that out. Example bpm cell:
        # <td class="right poptip" data-stat="bpm" data-tip="OBPM: -3.7&lt;br&gt; DBPM: -2.4&lt;
        # br&gt; VORP: -3.2&lt;br&gt; &lt;em&gt;&lt;small&gt;VORP is prorated to 82 games&lt;
        # /small&gt;&lt;/em&gt; ">-6.1</td></tr>'
        re_bpm = r"data-stat=\"bpm\".+OBPM: (?P<obpm>[0-9.-]+)&.+DBPM: (?P<dbpm>[0-9-.]+)&.+VORP: (?P<vorp>[0-9-.]+)&.+>(?P<bpm>[0-9-.]+)</td>"

        player_stats = dict()
        for line in stat_list:
            # this splits off the table header information for each row, which contains all of the player
            # information, name and id. The stat group contains the <tr> sections that correspond to each
            # players basic statistics
            split_header = line.split("</th>")
            name_group = split_header[0]
            stat_group = split_header[1]

            player_info = re.search(re_player_info, name_group)
            parsed_stats = re.findall(re_stats, stat_group)
            stat_dict = dict()
            for s in parsed_stats:
                if s[0] in bbref_to_pstat_map_advanced.keys():
                    stat_dict[bbref_to_pstat_map_advanced[s[0]]] = s[1]
            bpm_parse = re.search(re_bpm, stat_group)
            if bpm_parse is not None:
                stat_dict["bpm"] = bpm_parse.group("bpm")
                stat_dict["obpm"] = bpm_parse.group("obpm")
                stat_dict["dbpm"] = bpm_parse.group("dbpm")
                stat_dict["vorp"] = bpm_parse.group("vorp")

            for _, v in bbref_to_pstat_map_advanced.items():
                if stat_dict.get(v, None) is None:
                    stat_dict[v] = 0
            player_stats[player_info.group("id")] = stat_dict
        return player_stats

    @staticmethod
    def time_string_to_hours(time: str) -> float:
        # Transforms time from 40:53 -> 40.8833
        split = time.split(":")
        return str(int(split[0]) + (int(split[1]) / 60))

    def parse_team_stats(self, response, team_abbr: str):
        # xpath is dynamically named after the teams abbreviation, so that needs to get passed into the
        # function so that we can accurately pull statistics. Team stats are found in foot of table
        # and xpath will return a list of stats to parse
        basic_xpath_str = '//table[@id="box-' + team_abbr + '-game-basic"]//tfoot//td'
        advanced_xpath_str = (
            '//table[@id="box-' + team_abbr + '-game-advanced"]//tfoot//td'
        )

        # something is strange with the html in the four_fact and scoreline tables, scrapy
        # is unable to find the link when referencing the id directly to the table. The
        # current workaround will use the string comment from the section above the table
        # which has all the required data.
        four_factor_xpath = '//div[@id="all_four_factors"]/comment()'
        scoreline_xpath = '//div[@id="all_line_score"]/comment()'

        basic_box = response.xpath(basic_xpath_str).getall()
        advanced_box = response.xpath(advanced_xpath_str).getall()
        four_factor = response.xpath(four_factor_xpath).get()
        scoreline = response.xpath(scoreline_xpath).get()

        team_stat_dict = {}
        team_stat_dict.update(self.parse_basic_team(basic_box))
        team_stat_dict.update(self.parse_advanced_team(advanced_box))
        team_stat_dict.update(self.parse_four_factor(four_factor, team_abbr))
        team_stat_dict.update(self.parse_scoreline(scoreline, team_abbr))

        return team_stat_dict

    def parse_basic_team(self, basic_box: List[str]) -> dict:
        # basic_box is a list of cells from the basic box score table
        # each looks like this '<td class="right " data-stat="mp">240</td>'

        # maps the field names from basketball reference  basic boxscore to the expected
        # field name specified in the spacy TeamStats object.
        bbref_to_teamstat_map = {
            "fg": "fgm",
            "fga": "fga",
            "fg_pct": "fg_per",
            "fg3": "x3pm",
            "fg3a": "x3pa",
            "fg3_pct": "x3p_per",
            "ft": "ftm",
            "fta": "fta",
            "ft_pct": "ft_per",
            "orb": "orebs",
            "drb": "drebs",
            "trb": "rebounds",
            "ast": "assists",
            "stl": "steals",
            "blk": "blocks",
            "tov": "turnovers",
            "pf": "fouls",
            "pts": "points",
        }
        return self.parse_team_box(basic_box, bbref_to_teamstat_map)

    def parse_advanced_team(self, advanced_box: str) -> dict:
        # advanced_box is a list of cells from the advanced box score table
        # each looks like this '<td class="right " data-stat="mp">240</td>'

        # maps the field names from basketball reference advanced boxscore to the expected
        # field name specified in the spacy TeamStats object.
        bbref_to_teamstat_map = {
            "ts_pct": "ts_per",
            "efg_pct": "efg_per",
            "fg3a_per_fga_pct": "x3p_ar",
            "fta_per_fga_pct": "ft_ar",
            "orb_pct": "oreb_per",
            "drb_pct": "dreb_per",
            "trb_pct": "reb_per",
            "ast_pct": "ast_per",
            "stl_pct": "stl_per",
            "blk_pct": "blk_per",
            "tov_pct": "tov_per",
            "usg_pct": "usg_per",
            "off_rtg": "off_rating",
            "def_rtg": "def_rating",
        }
        return self.parse_team_box(advanced_box, bbref_to_teamstat_map)

    @staticmethod
    def parse_team_box(table_str: List[str], stat_map: dict) -> dict:
        stats = {}
        for stat in table_str:
            match = re.search(
                r"data-stat=\"(?P<stat>[A-Za-z0-9_]+)\">(?P<val>[0-9.]+)<", stat
            )
            if not match:
                continue
            if match.group("stat") in stat_map.keys():
                stats[stat_map.get(match.group("stat"))] = match.group("val")
        return stats

    @staticmethod
    def parse_four_factor(four_factor: str, abbr: str) -> dict:
        # map for stats in the four factor group to map to scrapy fields
        bbref_to_teamstat_map = {"pace": "pace", "ft_rate": "ft_per_fga"}
        # FourFactor is a string comment from the html that contains all the stats since the html
        # table can't be found via xpath. Below regex path will pull the four factor stats for the
        # given team.
        # Sample string:
        #     'NJN</a></th><td class="right " data-stat="pace" >93.2</td><td class="right minus"
        #     data-stat="efg_pct" >.395</td><td class="right plus" data-stat="tov_pct" >13.8</td>
        #     <td class="right minus" data-stat="orb_pct" >12.5</td><td class="right plus" data-stat="ft_rate" >
        #     .224</td><td class="right " data-stat="off_rtg" >82.6</td></tr><tr ><th scope="row" class="left "
        #     data-stat="team_id" >'
        clean_str = four_factor.replace("/n", "")
        re_str = abbr + r"<.+(?=\<a)|" + abbr + r"<.+(?=</tr)"
        snippet = re.search(re_str, clean_str)

        # Given the snippet, this will return a list of tuples [(stat, value)] with the stat values
        # returns:
        #   [('pace', '93.2'),
        #  ('efg_pct', '.395'),
        #  ('tov_pct', '13.8'),
        #  ('orb_pct', '12.5'),
        #  ('ft_rate', '.224'),
        #  ('off_rtg', '82.6')]

        stats = re.findall(
            r"data-stat=\"(?P<stat>[A-Za-z0-9_]+)\" >(?P<val>[0-9.]+)<", snippet.group()
        )
        stat_dict = dict()
        for stat in stats:
            if stat[0] in bbref_to_teamstat_map.keys():
                stat_dict[bbref_to_teamstat_map.get(stat[0])] = stat[1]
        return stat_dict

    @staticmethod
    def parse_scoreline(scoreline: str, abbr: str) -> dict:
        # map for stats in the four factor group to map to scrapy fields
        bbref_to_teamstat_map = {
            "1": "x1q_pts",
            "2": "x2q_pts",
            "3": "x3q_pts",
            "4": "x4q_pts",
        }

        ot_match = r"[0-9]OT"
        # scoreline is a string comment from the html that contains all the stats since the html
        # table can't be found via xpath. Below regex path will pull the four factor stats for the
        # given team.
        # Sample string:
        #     'NJN</a></th><td class="right " data-stat="pace" >93.2</td><td class="right minus"
        #     data-stat="efg_pct" >.395</td><td class="right plus" data-stat="tov_pct" >13.8</td>
        #     <td class="right minus" data-stat="orb_pct" >12.5</td><td class="right plus" data-stat="ft_rate" >
        #     .224</td><td class="right " data-stat="off_rtg" >82.6</td></tr><tr ><th scope="row" class="left "
        #     data-stat="team_id" >'
        clean_str = scoreline.replace("/n", "")
        re_str = abbr + r"<.+(?=<a)|" + abbr + r"<.+(?=</tr)"
        snippet = re.search(re_str, clean_str)

        # Given the snippet, this will return a list of tuples [(stat, value)] with the stat values
        # returns:
        #   [('1', '25'),
        #  ('2', '25'),
        #  ('3', '25'),
        #  ('4', '25'),
        #  ('1OT', '25'),
        #  ('T', '125')]

        stats = re.findall(
            r"data-stat=\"(?P<stat>[A-Za-z0-9_]+)\" >(?P<val>[0-9.]+)<", snippet.group()
        )
        stat_dict = dict()
        stat_dict["ot_pts"] = 0
        for stat in stats:
            if stat[0] in bbref_to_teamstat_map.keys():
                stat_dict[bbref_to_teamstat_map.get(stat[0])] = stat[1]
            elif re.match(ot_match, stat[0]):
                stat_dict["ot_pts"] += int(stat[1])
        stat_dict["ot_pts"] = str(stat_dict["ot_pts"])
        return stat_dict

    @staticmethod
    def get_away_home_records(record_string: List[str], scores: List[int]):
        # record_string = ['away_wins-away_losses', 'home_wins'-'home_losses']
        # scores = [away_score, home_score]
        split_away = record_string[0].split(
            "-"
        )  # results in ['away_wins', 'away_losses']
        split_home = record_string[1].split(
            "-"
        )  # results in ['home_wins', 'home_losses']

        # BasketballReference record includes the result of the game in question
        # we need to determine game winner and update the record values for wins
        # and losses to get an accurate record up to, but not including the current game.
        away_losses = (
            split_away[1] if scores[0] > scores[1] else str(int(split_away[1]) - 1)
        )
        away_wins = (
            split_away[0] if scores[0] < scores[1] else str(int(split_away[0]) - 1)
        )

        home_losses = (
            split_home[1] if scores[1] > scores[0] else str(int(split_home[1]) - 1)
        )
        home_wins = (
            split_home[0] if scores[1] < scores[0] else str(int(split_home[0]) - 1)
        )

        away_record = Record(wins=away_wins, losses=away_losses)
        home_record = Record(wins=home_wins, losses=home_losses)
        return away_record, home_record
