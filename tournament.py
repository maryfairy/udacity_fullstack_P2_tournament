#Tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteMatches():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    query = "DELETE FROM matches"
    c.execute(query)
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    query = "DELETE FROM players"
    c.execute(query)
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    """Need to return as an integer, avoiding the L requires declaring integer."""
    query = "SELECT count(id) FROM players;"
    c.execute(query)
    rows = c.fetchall()
    db.close()
    return rows[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    param = (name,)
    c.execute(query, param)
    db.commit()
    db.close

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    query = "SELECT * FROM standings"
    c.execute(query)
    rows = c.fetchall()
    db.close()
    return rows

def playerByes():
    """Returns a list of players who have already had byes.
    """
    db = connect()
    c = db.cursor()
    query = "SELECT * from matches WHERE loser IS NULL"
    c.execute(query)
    rows = c.fetchall()
    db.close()
    bye_ids = []
    for i in range(len(rows)):
        player_id = rows[i][1]
        bye_ids.append(player_id)
    return bye_ids

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    query = "INSERT INTO matches (winner,loser) VALUES (%s, %s)"
    param = (winner,loser)
    c.execute(query, param)
    db.commit()
    db.close

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect()
    c = db.cursor()
    query = "SELECT * FROM standings"
    c.execute(query)
    standings = c.fetchall()
    """ below is just standings ranking last place as first row, used to pick
    the best candidate for the BYE as well as to cycle through checking
    who's had a bye.
    """
    query = "SELECT * FROM standings ORDER BY wins ASC"
    c.execute(query)
    reversed_standings = c.fetchall()


    pairings = []
    """ Create empty array. Used later to remove the player with a BYE from 
    the standings table. All remaining players written to this table to
    cycle through SwissPairings.
    """
    new_standings = []

    """ Empty list, will return the player with the BYE for the round."""
    new_bye_id = []

    c = countPlayers()

    """ List of players who already have BYEs."""

    bye_ids = playerByes()

    """ If the number of players in the tournament is odd, proceed to find player for BYE"""
    if c % 2 == 1:
        for i in range(len(reversed_standings)):
                if len(new_bye_id) == 0 and reversed_standings[i][0] not in bye_ids:
                    new_bye_id.append(reversed_standings[i][0])
                else:
                    pass
        if len(new_bye_id) == 0:
            """ Defaults to let tournament organizer know all players have had a BYE"""
            print('All players have had a BYE.')
    """ this populates the new_standings table without the player with a BYE to sort"""
    for i in range(len(standings)):
        if len(standings) % 2 == 0:
            new_standings = standings
        elif new_bye_id[0] == standings[i][0]:
            new_bye_pairing = standings[i]
        else:
            new_standings.append(standings[i])
    for i in range(len(new_standings)):
        r = len(new_standings)
        if i == 0 or i % 2 ==0:
            pair = new_standings[i][0], new_standings[i][1], \
                   new_standings[i+1][0], new_standings[i+1][1]
            pairings.append(pair)
    """ if there is a player with a BYE, append them to the end of the SwissPairing output"""
    if len(new_bye_id) > 0:
        pair = new_bye_pairing[0], new_bye_pairing[1], \
           None
        pairings.append(pair)
    return pairings
