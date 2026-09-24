from pathlib import Path
import sys
from fm2001_data import FM2001Database

def main():
    game_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Games\FM2001')
    db = FM2001Database(game_dir)
    assert len(db.clubs) == 1246
    assert len(db.players) == 30064
    assert len(db.managers) == 1612
    assert len(db.positions) == 20
    assert db.clubs[0].name == 'Arsenal'
    assert db.players[0].full_name == 'David Seaman'
    assert db.players[0].club_id == 0
    assert db.players[2].full_name == 'Nigel Winterburn'
    assert db.clubs[db.players[2].club_id].name == 'West Ham United'
    assert db.managers[10].full_name == 'Alex Ferguson'
    assert db.managers[10].date_of_birth.isoformat() == '1941-12-31'
    assert db.managers[204].full_name == 'Arsène Wenger'
    assert db.managers[204].club_id == 0
    print('FM2001 clean-room parser verification passed')
    print(db.summary())

if __name__ == '__main__':
    main()
