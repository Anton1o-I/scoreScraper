from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Boolean,
    Integer,
    String,
    Float,
    Date,
    MetaData,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from game_crawlers.nba.seasons import Seasons
from datetime import datetime
import pytz
from typing import List


Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)
    date = Column(Date, nullable=False)
    season = Column(String)
    regular_season = Column(Boolean)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    over_under = Column(Integer)
    favorite = Column(String)
    spread = Column(Integer)
    team_stats = relationship("TeamStat", back_populates="game", cascade="save-update")
    player_stats = relationship(
        "PlayerStat", back_populates="game", cascade="save-update"
    )


class Team(Base):
    __tablename__ = "teams"

    abbr = Column(String, primary_key=True)
    location = Column(String, nullable=False)
    name = Column(String, nullable=False)
    game_stats = relationship("TeamStat", back_populates="team")
    player_stats = relationship("PlayerStat")


class TeamStat(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True)
    game_id = Column(String, ForeignKey("games.id"))
    game = relationship("Game", back_populates="team_stats")
    team_abbr = Column(String, ForeignKey("teams.abbr"))
    team = relationship("Team", back_populates="game_stats", cascade="save-update")
    home = Column(Boolean)
    fgm = Column(Integer)
    fga = Column(Integer)
    fg_per = Column(Float)
    x3pa = Column(Integer)
    x3pm = Column(Integer)
    x3p_per = Column(Float)
    fta = Column(Integer)
    ftm = Column(Integer)
    ft_per = Column(Float)
    orebs = Column(Integer)
    drebs = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    fouls = Column(Integer)
    points = Column(Integer)
    x1q_pts = Column(Integer)
    x2q_pts = Column(Integer)
    x3q_pts = Column(Integer)
    x4q_pts = Column(Integer)
    ot_pts = Column(Integer)
    pace = Column(Float)  # Four Factor Table
    efg_per = Column(Float)
    to_per = Column(Float)  # Four Factor Table
    orb_per = Column(Float)
    ft_per_fga = Column(Float)  # Four Factor table
    off_rating = Column(Float)
    ts_per = Column(Float)
    x3p_ar = Column(Float)
    ft_ar = Column(Float)
    oreb_per = Column(Float)
    dreb_per = Column(Float)
    reb_per = Column(Float)
    ast_per = Column(Float)
    stl_per = Column(Float)
    blk_per = Column(Float)
    tov_per = Column(Float)
    usg_per = Column(Float)
    off_rating = Column(Float)
    def_rating = Column(Float)


class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    stats = relationship("PlayerStat", back_populates="player")


class PlayerStat(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(String, ForeignKey("players.id"))
    player = relationship("Player", back_populates="stats", cascade="save-update")
    game_id = Column(String, ForeignKey("games.id"))
    game = relationship("Game", back_populates="player_stats")
    team_abbr = Column(String, ForeignKey("teams.abbr"))
    team = relationship("Team", back_populates="player_stats")
    minutes = Column(Float)
    points = Column(Integer)
    drebs = Column(Integer)
    orebs = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    turnovers = Column(Integer)
    fgm = Column(Integer)
    fga = Column(Integer)
    fg_per = Column(Float)
    ftm = Column(Integer)
    fta = Column(Integer)
    ft_per = Column(Float)
    x3pm = Column(Integer)
    x3pa = Column(Integer)
    x3p_per = Column(Float)
    blocks = Column(Integer)
    steals = Column(Integer)
    fouls = Column(Integer)
    plus_minus = Column(Integer)
    ts_per = Column(Float)
    efg_per = Column(Float)
    x3p_ar = Column(Float)
    ft_ar = Column(Float)
    oreb_per = Column(Float)
    dreb_per = Column(Float)
    reb_per = Column(Float)
    ast_per = Column(Float)
    stl_per = Column(Float)
    blk_per = Column(Float)
    tov_per = Column(Float)
    usg_per = Column(Float)
    off_rating = Column(Float)
    def_rating = Column(Float)
    bpm = Column(Float)
    obpm = Column(Float)
    dbpm = Column(Float)
    vorp = Column(Float)


class nbaDB:
    def __init__(self, user, password):
        self.engine = create_engine(
            f"postgresql://{user}:{password}@localhost:5432/nba_stats", echo=False
        )
        Sess = sessionmaker(bind=self.engine)
        self.session = Sess()

    def add_record(self, record: dict):
        team_data = record.get("team_stats")
        player_data = record.get("player_stats")
        g = self.map_to_db(record)
        ps = self.map_player_stats(
            player_data,
            team_data.get("home_stats", {}).get("team", {}).get("abbreviation", ""),
            team_data.get("away_stats", {}).get("team", {}).get("abbreviation", ""),
        )
        ts = self.map_team_stats(team_data)

        players = self.map_players(player_data)
        teams = self.map_teams(team_data)

        for p in players:
            instance = self.session.query(Player).filter(Player.id == p.id).first()
            if not instance:
                self.session.add(p)

        for t in teams:
            instance = self.session.query(Team).filter(Team.abbr == t.abbr).first()
            if not instance:
                self.session.add(t)

        g.team_stats = ts
        g.player_stats = ps

        self.session.add(g)

    def __del__(self):
        self.session.close()
        print("nbaDB connection closed")

    def map_to_db(self, item: dict) -> Game:
        game_data = item.get("game_data")
        s = self.get_season(game_data.get("date", ""))
        rs = self.regular_season(game_data.get("date", ""), s)
        game = Game(
            id=game_data.get("game_id", ""),
            date=game_data.get("date", ""),
            season=s,
            regular_season=rs,
            home_wins=game_data.get("home_record", {}).get("wins", ""),
            home_losses=game_data.get("home_record", {}).get("losses", ""),
            away_wins=game_data.get("away_record", {}).get("wins", ""),
            away_losses=game_data.get("away_record", {}).get("losses", ""),
        )
        return game

    @staticmethod
    def get_season(date: str) -> String:
        d = datetime.strptime(date, "%I:%M %p, %B %d, %Y").date()
        for k, v in Seasons.season_info.items():
            rss = v["regular_season_start"]
            pse = v["post_season_end"]
            if d >= rss.date() and d <= pse.date():
                return k

    @staticmethod
    def regular_season(date: str, season: str) -> Boolean:
        d = datetime.strptime(date, "%I:%M %p, %B %d, %Y").date()
        rss = Seasons.season_info[season]["regular_season_start"]
        rse = Seasons.season_info[season]["regular_season_end"]
        if d >= rss.date() and d <= rse.date():
            return True
        return False

    @staticmethod
    def map_player_stats(player_data, home_pk, away_pk) -> List[PlayerStat]:
        pk_map = {"home_stats": home_pk, "away_stats": away_pk}
        player_db_list = []
        # loops through the home and away team player stats.
        for k in player_data.keys():
            # loop through each player in the home and away team player stats list.
            for ps in player_data[k]:
                # create dictionary to pass to sqlalchemy object since most fields
                # match exactly between scrapy and psql.
                skip_field = ["player", "min"]
                pass_dict = {k: v for k, v in ps.items() if k not in skip_field}
                stat = PlayerStat(
                    player_id=ps.get("player", "")["player_id"],
                    team_abbr=pk_map[k],
                    minutes=ps.get("min", ""),
                    **pass_dict,
                )
                player_db_list.append(stat)
        return player_db_list

    @staticmethod
    def map_team_stats(team_data) -> List[TeamStat]:
        team_db_list = []
        for k in team_data.keys():
            team = team_data[k]
            # create dictionary to pass to sqlalchemy object since most fields
            # match exactly between scrapy and psql.
            skip_fields = ["game_id", "team", "home"]
            pass_dict = {k: v for k, v in team.items() if k not in skip_fields}
            team_stat = TeamStat(
                game_id=team.get("game_id", ""),
                team_abbr=team.get("team", {}).get("abbreviation", ""),
                home=True if (k == "home_stats") else False,
                **pass_dict,
            )
            team_db_list.append(team_stat)
        return team_db_list

    @staticmethod
    def map_players(player_data) -> List[Player]:
        players = []
        for k in player_data.keys():
            for p in player_data[k]:
                player = Player(
                    id=p.get("player", {}).get("player_id", ""),
                    first_name=p.get("player", {}).get("first_name", ""),
                    last_name=p.get("player", {}).get("last_name", ""),
                )
                players.append(player)
        return players

    @staticmethod
    def map_teams(team_data) -> List[Team]:
        teams = []
        for k in team_data.keys():
            t = team_data[k]
            team = Team(
                location=t.get("team", {}).get("location", ""),
                name=t.get("team", {}).get("name", ""),
                abbr=t.get("team", {}).get("abbreviation", ""),
            )
            teams.append(team)
        return teams
