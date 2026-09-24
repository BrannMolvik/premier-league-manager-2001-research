from pathlib import Path
import sys
from fm2001_data import FM2001Database
from competition_state import PremierLeagueState

def main():
    game_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Games\FM2001')
    db = FM2001Database(game_dir)
    assert len(db.clubs) == 1246
    assert len(db.players) == 30064
    assert len(db.managers) == 1612
    assert len(db.positions) == 20
    assert len(db.rounds) == 1053
    assert len(db.premier_league_rounds) == 38
    assert len(db.real_fixtures) == 380
    assert len({f.round_index for f in db.real_fixtures}) == 38
    assert all(len(db.fixtures_for_round(r)) == 10 for r in range(38))
    pl_clubs = {c for f in db.real_fixtures for c in (f.home_club_id, f.away_club_id)}
    assert len(pl_clubs) == 20
    assert all(sum(1 for f in db.real_fixtures if f.home_club_id == c) == 19 for c in pl_clubs)
    assert all(sum(1 for f in db.real_fixtures if f.away_club_id == c) == 19 for c in pl_clubs)
    league = PremierLeagueState(db.real_fixtures, db.premier_league_rounds, 2000)
    assert league.round_date(0).isoformat() == '2000-08-19'
    assert league.round_date(1).isoformat() == '2000-08-23'
    assert league.round_date(18).isoformat() == '2000-12-26'
    assert league.round_date(20).isoformat() == '2001-01-01'
    assert league.round_date(37).isoformat() == '2001-05-20'
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
