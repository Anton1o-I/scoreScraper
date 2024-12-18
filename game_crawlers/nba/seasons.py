from dataclasses import dataclass
from datetime import datetime


@dataclass
class Seasons:
    season_info = {
         "90-91": {
            "regular_season_start": datetime(1990, 11, 2),
            "regular_season_end": datetime(1991, 4, 21),
            "post_season_start": datetime(1991, 4, 25),
            "post_season_end": datetime(1991, 6, 12),
        },          
        "91-92": {
            "regular_season_start": datetime(1991, 11, 1),
            "regular_season_end": datetime(1992, 4, 19),
            "post_season_start": datetime(1992, 4, 23),
            "post_season_end": datetime(1992, 6, 14),
        },   
        "92-93": {
            "regular_season_start": datetime(1992, 11, 6),
            "regular_season_end": datetime(1993, 4, 25),
            "post_season_start": datetime(1993, 4, 29),
            "post_season_end": datetime(1993, 6, 20),
        },             
        "93-94": {
            "regular_season_start": datetime(1993, 11, 5),
            "regular_season_end": datetime(1994, 4, 24),
            "post_season_start": datetime(1994, 4, 28),
            "post_season_end": datetime(1994, 6, 22),
        },               
        "94-95": {
            "regular_season_start": datetime(1994, 11, 4),
            "regular_season_end": datetime(1995, 4, 23),
            "post_season_start": datetime(1995, 4, 27),
            "post_season_end": datetime(1995, 6, 14),
        },        
        "95-96": {
            "regular_season_start": datetime(1995, 11, 3),
            "regular_season_end": datetime(1996, 4, 21),
            "post_season_start": datetime(1996, 4, 25),
            "post_season_end": datetime(1996, 6, 16),
        },
        "96-97": {
            "regular_season_start": datetime(1996, 11, 1),
            "regular_season_end": datetime(1997, 4, 20),
            "post_season_start": datetime(1997, 4, 24),
            "post_season_end": datetime(1997, 6, 13),
        },
        "97-98": {
            "regular_season_start": datetime(1997, 10, 31),
            "regular_season_end": datetime(1998, 4, 19),
            "post_season_start": datetime(1998, 4, 23),
            "post_season_end": datetime(1998, 6, 14),
        },
        "98-99": {
            "regular_season_start": datetime(1999, 2, 5),
            "regular_season_end": datetime(1999, 5, 5),
            "post_season_start": datetime(1999, 5, 8),
            "post_season_end": datetime(1999, 6, 25),
        },
        "99-00": {
            "regular_season_start": datetime(1999, 11, 2),
            "regular_season_end": datetime(2000, 4, 19),
            "post_season_start": datetime(2000, 4, 22),
            "post_season_end": datetime(2000, 6, 19),
        },
        "00-01": {
            "regular_season_start": datetime(2000, 10, 31),
            "regular_season_end": datetime(2001, 4, 18),
            "post_season_start": datetime(2001, 4, 21),
            "post_season_end": datetime(2001, 6, 15),
        },
        "01-02": {
            "regular_season_start": datetime(2001, 10, 30),
            "regular_season_end": datetime(2002, 4, 17),
            "post_season_start": datetime(2002, 4, 20),
            "post_season_end": datetime(2002, 6, 12),
        },
        "02-03": {
            "regular_season_start": datetime(2002, 10, 29),
            "regular_season_end": datetime(2003, 4, 16),
            "post_season_start": datetime(2003, 4, 19),
            "post_season_end": datetime(2003, 6, 15),
        },
        "03-04": {
            "regular_season_start": datetime(2003, 10, 28),
            "regular_season_end": datetime(2004, 4, 14),
            "post_season_start": datetime(2004, 4, 17),
            "post_season_end": datetime(2004, 6, 15),
        },
        "04-05": {
            "regular_season_start": datetime(2004, 11, 2),
            "regular_season_end": datetime(2005, 4, 20),
            "post_season_start": datetime(2005, 4, 23),
            "post_season_end": datetime(2005, 6, 23),
        },
        "05-06": {
            "regular_season_start": datetime(2005, 11, 1),
            "regular_season_end": datetime(2006, 4, 19),
            "post_season_start": datetime(2006, 4, 22),
            "post_season_end": datetime(2006, 6, 3),
        },
        "06-07": {
            "regular_season_start": datetime(2006, 10, 31),
            "regular_season_end": datetime(2007, 4, 18),
            "post_season_start": datetime(2007, 4, 21),
            "post_season_end": datetime(2007, 6, 14),
        },
        "07-08": {
            "regular_season_start": datetime(2007, 10, 30),
            "regular_season_end": datetime(2008, 4, 16),
            "post_season_start": datetime(2008, 4, 19),
            "post_season_end": datetime(2008, 6, 17),
        },
        "08-09": {
            "regular_season_start": datetime(2008, 10, 28),
            "regular_season_end": datetime(2009, 4, 16),
            "post_season_start": datetime(2009, 4, 18),
            "post_season_end": datetime(2009, 6, 14),
        },
        "09-10": {
            "regular_season_start": datetime(2009, 10, 27),
            "regular_season_end": datetime(2010, 4, 14),
            "post_season_start": datetime(2010, 4, 17),
            "post_season_end": datetime(2010, 6, 17),
        },
        "10-11": {
            "regular_season_start": datetime(2010, 10, 26),
            "regular_season_end": datetime(2011, 4, 13),
            "post_season_start": datetime(2011, 4, 16),
            "post_season_end": datetime(2011, 6, 12),
        },
        "11-12": {
            "regular_season_start": datetime(2011, 12, 25),
            "regular_season_end": datetime(2012, 4, 26),
            "post_season_start": datetime(2012, 4, 28),
            "post_season_end": datetime(2012, 6, 21),
        },
        "12-13": {
            "regular_season_start": datetime(2012, 10, 30),
            "regular_season_end": datetime(2013, 4, 17),
            "post_season_start": datetime(2013, 4, 20),
            "post_season_end": datetime(2013, 6, 20),
        },
        "13-14": {
            "regular_season_start": datetime(2013, 10, 29),
            "regular_season_end": datetime(2014, 4, 16),
            "post_season_start": datetime(2014, 4, 19),
            "post_season_end": datetime(2014, 6, 15),
        },
        "14-15": {
            "regular_season_start": datetime(2014, 10, 28),
            "regular_season_end": datetime(2015, 4, 15),
            "post_season_start": datetime(2015, 4, 18),
            "post_season_end": datetime(2015, 6, 16),
        },
        "15-16": {
            "regular_season_start": datetime(2015, 10, 27),
            "regular_season_end": datetime(2016, 4, 13),
            "post_season_start": datetime(2016, 4, 16),
            "post_season_end": datetime(2016, 6, 19),
        },
        "16-17": {
            "regular_season_start": datetime(2016, 10, 25),
            "regular_season_end": datetime(2017, 4, 12),
            "post_season_start": datetime(2017, 4, 15),
            "post_season_end": datetime(2017, 6, 12),
        },
        "17-18": {
            "regular_season_start": datetime(2017, 10, 17),
            "regular_season_end": datetime(2018, 4, 11),
            "post_season_start": datetime(2018, 4, 14),
            "post_season_end": datetime(2018, 6, 8),
        },
        "18-19": {
            "regular_season_start": datetime(2018, 10, 16),
            "regular_season_end": datetime(2019, 4, 10),
            "post_season_start": datetime(2019, 4, 13),
            "post_season_end": datetime(2019, 6, 13),
        },
        "19-20": {
            "regular_season_start": datetime(2019, 10, 22),
            "regular_season_end": datetime(2020, 8, 14),
            "post_season_start": datetime(2020, 8, 15),
            "post_season_end": datetime(2020, 10, 11),
        },
        "20-21": {
            "regular_season_start": datetime(2020, 12, 22),
            "regular_season_end": datetime(2021, 5, 16),
            "post_season_start": datetime(2021, 5, 18),
            "post_season_end": datetime(2021, 7, 20),
        },
        "21-22": {
            "regular_season_start": datetime(2021, 10, 19),
            "regular_season_end": datetime(2022, 4, 10),
            "post_season_start": datetime(2022, 4, 12),
            "post_season_end": datetime(2022, 6, 16),
        },
        "22-23": {
            "regular_season_start": datetime(2022, 10, 18),
            "regular_season_end": datetime(2023, 4, 9),
            "post_season_start": datetime(2023, 4, 11),
            "post_season_end": datetime(2023, 6, 12),
        },
        "23-24": {
            "regular_season_start": datetime(2023, 10, 24),
            "regular_season_end": datetime(2024, 4, 14),
            "post_season_start": datetime(2024, 4, 16),
            "post_season_end": datetime(2024, 6, 17),
        },
     }
