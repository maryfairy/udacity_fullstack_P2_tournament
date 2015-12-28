--- Tables and views create for tournament
-- Create database first, then at least 2 tables, players and matches
-- May require you to create Views, been having issues passing tests using views, so we shall see

-- Need to DROP/DELETE tables during design to make sure we pass the tests
DROP DATABASE IF EXISTS tournament;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP VIEW IF EXISTS standings CASCADE;
DROP VIEW IF EXISTS player_win_count CASCADE;
DROP VIEW IF EXISTS player_match_count CASCADE;
DROP VIEW IF EXISTS player_omw CASCADE;

-- Create a DB to connect to
CREATE DATABASE tournament;
\connect tournament;

-- Create two tables, list of players and a list of matches
CREATE TABLE players(
        id SERIAL PRIMARY KEY,
        name TEXT
);

CREATE TABLE matches(
        id SERIAL PRIMARY KEY, --note to self, originally, using PRIMARY KEY (winner, loser), screwed up allowin NULL constraint for loser in BYE EC
        winner INTEGER NOT NULL references players(id),
        loser INTEGER NULL references players(id)

);

-- create two views to summarize players positions by wins and no. of matches
-- could have just place as subquery in standings, but breaking out looks neater 
CREATE VIEW player_win_count AS
SELECT
players.id as id, count(matches.winner) as win_count
FROM players
LEFT JOIN matches on players.id = matches.winner
GROUP BY 1
;

CREATE VIEW player_match_count AS
SELECT
players.id as id,
count(matches.winner) + count(matches.loser) as match_count
FROM players
LEFT JOIN matches on players.id = matches.winner OR
players.id = matches.loser
GROUP BY 1
;


-- view outputs list of players with their opponents' win total used to sort standings
-- query can likely be simplified
CREATE VIEW player_omw AS
SELECT
players_opps.player_id as id,
sum(win_count.win_count)  as omw

FROM
 (SELECT player_id, opponent

         FROM
         (SELECT p.id as player_id, m.winner as opponent FROM
        players p
        LEFT JOIN
        matches m
        on p.id = m.loser
        GROUP BY 1,2
        ) opp_wins

        UNION ALL

        SELECT
        player_id,opponent
        FROM
             (SELECT p.id as player_id, m.loser as opponent FROM
            players p
            LEFT JOIN
            matches m
            on p.id = m.winner
            GROUP BY 1,2
            ) opp_loses

    WHERE opponent IS NOT NULL
    ) players_opps

LEFT JOIN player_win_count win_count on win_count.id = players_opps.opponent
GROUP BY 1
ORDER BY 1 asc;

-- final view is for standings (depends on omw)
CREATE VIEW standings AS
SELECT
players.id as id,
players.name as name,
player_win_count.win_count as wins,
case when player_match_count.match_count = 0 then 0
        else player_match_count.match_count -1 end as matches

FROM players
LEFT JOIN player_win_count on players.id = player_win_count.id
LEFT JOIN player_match_count on players.id = player_match_count.id
LEFT JOIN player_omw omw on players.id = omw.id
ORDER BY wins desc, omw desc, name asc
;
