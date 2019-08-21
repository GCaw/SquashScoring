
class GameError(Exception):
    pass

class player():
    def __init__(self, name="default", side=0):
        self.name = name
        self.def_side = side

class rally():
    def __init__(self, winner=None, sideserved=None, extra=None):
        self.winner = winner
        self.sideserved = sideserved
        self.extra = extra

class squash_match():
    scoringtypes = ['par', 'old']
    endmatchtypes = ['normal', 'max', 'none']
    endgametypes = ['wb2', 'choice']
    validplayers = [0, 1, None]
    validsideserved = [0, 1, None] # 0 = Right, 1 = Left

    def __init__(self, scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2'):
        '''
            scoring:
                par (point a rally)
                old (only win points when serving)
            endmatchscore:
                number of games to win a match
            endmatchtype:
                normal (first to endmatchscore)
                max (total games played is maximized based on endmatchscore)
                none (free play)
            endgamescore:
                number of points to win a game
            endgametype:
                wb2 (win by two)
                choice (first to endgamescore-1 chooses to finish game at endgamescore+1 or endgamescore+2)
        '''
        self.firstserver = 0
        self.score = [[0,0]]
        self.server = 0
        self.servingside = 0
        self.choice = [0]

        self.scoring = scoring
        self.endmatchscore = endmatchscore
        self.endmatchtype = endmatchtype
        self.endgamescore = endgamescore
        self.endgametype = endgametype
        self.rallies = [rally(sideserved=0)]
        self.confirmgametypes()
        self.players = [player(), player()]

    def confirmgametypes(self):
        '''
           Sanity check to ensure you're not creating an imposisble game.
        '''
        if not (self.scoring in squash_match.scoringtypes):
            raise GameError("invalid score type: " +str(self.scoring))
        if not (self.endmatchtype in squash_match.endmatchtypes):
            raise GameError("invalid match end type: " +str(self.endmatchtype))
        if not (self.endgametype in squash_match.endgametypes):
            raise GameError("invalid game end type: " +str(self.endgametype))
        return True

    def otherserver(self, server):
        '''
            Server is either 1 or 0, return the opposite of provided.
        '''
        return int(not server)

    def changefirstserver(self):
        '''
            Before the first rally has completed, the server can be changed from
             the default depending on who is serving first
        '''
        if len(self.rallies) == 1:
            self.firstserver = self.otherserver(self.firstserver)
            self.server = self.firstserver
        else:
            raise GameError("Cannot change first server after first rally complete")

    def __updateserver(self):
        '''
            After every rally we must update who is serving.
            Call when updating the score
        '''
        if (self.ismatchover()):
            self.server = None
        else:
            self.server = self.rallies[-1].winner

    def __rallystart(self, side):
        '''
            Add a new rally to the list with specified serving side
        '''
        if (side in squash_match.validsideserved):
            self.rallies.append(rally(None,side,None))
        else:
            raise GameError("invalid side assigned to rally: " + str(side))

    def rallycomplete(self, winner=None, extra=None):
        '''
            Call this function each time a rally finishes, specifying who
             won the rally, as well as any other applicable info.
        '''
        if not (winner in squash_match.validplayers):
            raise GameError("invalid player assigned to rally " + str(winner))

        if not self.ismatchover():
            self.rallies[-1].winner = winner
            self.rallies[-1].extra = extra
            self.__updatescore()
            self.__rallystart(self.__whichsidetoserve())
        else:
            raise GameError("additional rally after match has finished")

    def __whichsidetoserve(self):
        '''
            Based on who has won previous rallies and from which side
             determine which side the next rally is to be served from.
        '''
        # are we replaying the previous rally?
        if (self.rallies[-1].winner == None):
            return self.rallies[-1].sideserved

        # did the winner serve last?
        if (self.rallies[-1].winner == self.__lastwinner()):
            return self.otherside(self.rallies[-1].sideserved)
        else:
            return self.players[self.rallies[-1].winner].def_side

    def __lastwinner(self):
        '''
            The rally list might have multiple rallies without a winner. For
             serving we need to know who last won the rally so we iterate
             through the list backwards looking for the last winner.
        '''
        winner = None
        i = len(self.rallies) - 2
        while (winner == None):
            if (self.rallies[i].winner == None):
                i -= 1
            else:
                return self.rallies[i].winner

            if (i == 0):
                raise GameError("we couldn't find a winner in the list of rallies")

    def undolastrally(self):
        '''
            Call this function to remove the last added rally
            Automatically calls __updatescore()
        '''
        if not (self.ismatchover()):
            del self.rallies[-2]
        else:
            del self.rallies[-1]

        self.__updatescore()

    def __updatescore(self):
        '''
            Each time a rally ends, or a change is made to the score
             call this function to update the scores and server
        '''
        self.score=[[0,0]]
        for i in range (len(self.rallies)):

            if self.rallies[i].winner is not None:
                if (self.scoring == 'par'):
                    self.score[-1][self.rallies[i].winner] +=1

                elif (self.scoring == 'old'):
                    if (i > 0):
                        if (self.rallies[i].winner == self.rallies[i-1].winner):
                            self.score[-1][self.rallies[i].winner] +=1
                    else:
                        if (self.rallies[i].winner == self.firstserver):
                            self.score[-1][self.rallies[i].winner] +=1

                else:
                    raise GameError("Invalid scoring type: " + str(scoring))

                if (self.isgameover()):
                    if (not self.ismatchover()):
                        self.score.append([0,0])
                        self.choice.append(0)

        self.__updateserver()
        
    def isgameover(self):
        '''
            Based on the type of game, determine whether the current game has completed.
        '''
        if (self.endgametype == 'wb2'):
            # in a win by two game, the game will be over if one player has a number of points larger
            #  than the end game score, and they have two or more points more than their opponent.
            if (   ((self.score[-1][0] >= self.endgamescore) and (self.score[-1][0] > self.score[-1][1] + 1))
                or ((self.score[-1][1] >= self.endgamescore) and (self.score[-1][1] > self.score[-1][0] + 1))):
                return True

        elif (self.endgametype == 'choice'):
            # in a choice game to 9, at 8 all, the first player to get 8 can chooise to play to 
            #  9 or 10 (a choice of 1 or 2). By default choice is set to 0.
            # Therefore if one player has the required score, the game has finished.
            if ((self.choice[-1] == 1) or (self.choice[-1] == 0)):
                if ((self.score[-1][0] == 9) or (self.score[-1][1] == 9)):
                    return True
            if (self.choice[-1] == 2):
                if ((self.score[-1][0] == 10) or (self.score[-1][1] == 10)):
                    return True
            
            if ((self.choice[-1] == 0) and ((self.score[-1][0] > 8) or (self.score[-1][1] > 8))):
                raise GameError("User should have chosen to play 1 or 2 points already but hasn't")

        else:
            raise GameError("Invalid endgametype specified: " + str(self.endgametype))

        return False
    
    def gameswon(self, player):
        '''
            Iterate through all the games and keep tabs of who has more
             points than the other (ie the winner) for each game.
        '''
        games = 0
        notplayer = not player

        for i in range (len(self.score)):
            # if it's not the last game
            if (not i == len(self.score) -1):
                if (self.score[i][player] > self.score[i][notplayer]):
                    games +=1

            # if it is the last game we first check if the game is over
            elif (self.isgameover()):
                if (self.score[i][player] > self.score[i][notplayer]):
                    games +=1
            
            else:
                pass

        return games

    def ismatchover(self):
        '''
            Based on the match end type, determine whether the match has finished
        '''
        if (self.endmatchtype == 'none'):
            # none implies free play, and no end to the match
            return False
        
        elif (self.endmatchtype == 'normal'):
            # a normal game ends when one player has the required number of games.
            if (   (self.endmatchscore == self.gameswon(0))
                or (self.endmatchscore == self.gameswon(1))):
                return True

        elif (self.endmatchtype == 'max'):
            # a max game ends when the max number of games is played.
            # e.g. A game to 3 (aka best out of 5) can take up to 5 games to complete,
            #  in this style of game we play 5 games, even if one player wins the first
            #  3 games.
            if ((self.gameswon(0) + self.gameswon(1)) == (self.endmatchscore *2 -1)):
                return True

        else:
            raise GameError("Invalid endmatchtype in use: " + str(self.endmatchtype))

        return False

    def setchoice(self, choice=1):
        '''
            When 8 all in a 'choice' game type, the player must select whether to play
             an additional point (2) or not (1)
        '''
        if ((choice == 1) or (choice == 2)):
            self.choice[-1] = choice
        else:
            raise GameError("Invalid choice provided: " + str(choice))

    def switch_serve_side(self):
        '''
            When starting to serve a player may change which side they serve on
        '''
        # @todo make robust to prevent change of serving side after starting to serve
        self.rallies[-1].sideserved = self.otherside(self.rallies[-1].sideserved)

    def otherside(self, side):
        '''
            Side is either 1 or 0, return the opposite of provided.
        '''
        return int(not side)