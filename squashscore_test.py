import pytest
from squashscore import squash_match, GameError

def test_basics(): 
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    match.rallycomplete(None, 'let')
    assert match.score == [[0,0]]
    assert len(match.rallies) == 2

    match.rallycomplete(1)
    assert match.score == [[0,1]]

    match.rallycomplete(0, 'stroke')
    assert match.score == [[1,1]]

def test_morebasics():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    match.rallycomplete(1)
    assert match.score == [[0,1]]

    match.rallycomplete(1)
    assert match.score == [[0,2]]

def test_scoring_old():
    match = squash_match(scoring='old',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    assert match.server == 0
    match.rallycomplete(0)

    assert match.score == [[1,0]]

    match.rallycomplete(1)
    match.rallycomplete(0)

    assert match.score == [[1,0]]

    match.rallycomplete(0)
    match.rallycomplete(0)

    assert match.score == [[3,0]]

    match.rallycomplete(1)
    match.rallycomplete(0)
    match.rallycomplete(1)
    match.rallycomplete(1)
    match.rallycomplete(1)

    assert match.score == [[3,2]]

def test_endgame_wb2():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    for i in range(11):
        match.rallycomplete(1)

    assert match.score == [[0,11],[0,0]]

    for i in range (10):
        match.rallycomplete(1)

    for i in range (11):
        match.rallycomplete(0)   

    for i in range(2):
        match.rallycomplete(1)

    for i in range(3):
        match.rallycomplete(0)

    assert match.score == [[0,11],[14,12],[0,0]]

def test_endgame_choice_normal():
    match = squash_match(scoring='old',endmatchscore=3,endmatchtype='none',endgamescore=9,endgametype='choice')
    assert match.score == [[0,0]]

    for i in range(9):
        match.rallycomplete(0)

    assert match.score == [[9,0],[0,0]]

def test_endgame_choice_two():
    match = squash_match(scoring='old',endmatchscore=3,endmatchtype='none',endgamescore=9,endgametype='choice')
    assert match.score == [[0,0]]

    for i in range(8):
        match.rallycomplete(0)

    for i in range(9):
        match.rallycomplete(1)

    match.setchoice(2)

    for i in range(2):
        match.rallycomplete(1)

    assert match.score == [[8,10],[0,0]]

def test_endgame_choice_one():
    match = squash_match(scoring='old',endmatchscore=3,endmatchtype='none',endgamescore=9,endgametype='choice')
    assert match.score == [[0,0]]

    for i in range(8):
        match.rallycomplete(0)

    for i in range(9):
        match.rallycomplete(1)

    match.setchoice(1)

    for i in range(1):
        match.rallycomplete(1)

    assert match.score == [[8,9],[0,0]]

def test_endmatch_none():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    for i in range (33):
        match.rallycomplete(1)

    for i in range (100):
        match.rallycomplete(0)

    assert match.gameswon(0) == 9
    assert match.gameswon(1) == 3

    assert match.score == [[0,11],[0,11],[0,11],[11,0],[11,0],[11,0],[11,0],[11,0],[11,0],[11,0],[11,0],[11,0],[1,0]]

    assert match.ismatchover() == False

def test_endmatch_normal():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='normal',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    for i in range (33):
        match.rallycomplete(1)

    assert match.gameswon(0) == 0
    assert match.gameswon(1) == 3

    assert match.score == [[0,11],[0,11],[0,11]]

    assert match.ismatchover() == True

def test_endmatch_max():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='max',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    for i in range (33):
        match.rallycomplete(1)

    assert match.gameswon(0) == 0
    assert match.gameswon(1) == 3

    assert match.score == [[0,11],[0,11],[0,11],[0,0]]

    assert match.ismatchover() == False

    for i in range (11):
        match.rallycomplete(1)
    
    assert match.gameswon(0) == 0
    assert match.gameswon(1) == 4

    assert match.score == [[0,11],[0,11],[0,11],[0,11],[0,0]]

    assert match.ismatchover() == False

    for i in range (11):
        match.rallycomplete(0)

    assert match.gameswon(0) == 1
    assert match.gameswon(1) == 4

    assert match.score == [[0,11],[0,11],[0,11],[0,11],[11,0]]

    assert match.ismatchover() == True

def test_undo():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.score == [[0,0]]

    for i in range (11):
        match.rallycomplete(1)

    match.undolastrally()
    assert match.score == [[0,10]]

    # @todo implement better testing

def test_server():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='normal',endgamescore=11,endgametype='wb2')
    assert match.server == 0

    match.changefirstserver()
    assert match.server == 1
    assert match.firstserver ==1

    match.changefirstserver()
    assert match.server == 0
    assert match.firstserver == 0

    match.rallycomplete(1)
    assert len(match.rallies) == 2
    assert match.rallies[-2].winner == 1
    assert match.server == 1

    match.rallycomplete(0)
    assert match.server == 0

    for i in range (11):
        match.rallycomplete(1)

    match.rallycomplete(0)
    assert match.server == 0

    assert match.score == [[1,11],[1,1]]
    
    for i in range (10):
        match.rallycomplete(0)

    assert match.score == [[1,11],[11,1],[0,0]]
    
    for i in range (22):
        match.rallycomplete(0)

    assert match.score == [[1,11],[11,1],[11,0],[11,0]]
    assert match.server == None

def test_server_exception():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.server == 0

    match.rallycomplete(0)
    assert match.server == 0

    with pytest.raises(GameError):
        match.changefirstserver()


def test_sideserve():
    match = squash_match(scoring='par',endmatchscore=3,endmatchtype='none',endgamescore=11,endgametype='wb2')
    assert match.rallies[-1].sideserved == 0

    match.switch_serve_side()
    assert match.rallies[-1].sideserved == 1

    match.rallycomplete(0)
    assert match.rallies[-1].sideserved == 0

    match.rallycomplete(0)
    assert match.rallies[-1].sideserved == 1

    match.rallycomplete(0)
    assert match.rallies[-1].sideserved == 0

    match.rallycomplete(1)
    assert match.rallies[-1].sideserved == 0

    match.rallycomplete(1)
    assert match.rallies[-1].sideserved == 1

    match.rallycomplete(1)
    assert match.rallies[-1].sideserved == 0