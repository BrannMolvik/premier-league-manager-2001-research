from __future__ import annotations
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from fm2001_data import FM2001Database, PLAYER_SKILLS
from human_gameplay import HumanGameplayController
from match_team_setup import TeamTacticalState

DEFAULT_GAME_DIR = Path(r'C:\Games\FM2001')

class App(tk.Tk):
    def __init__(self, game_dir: Path):
        super().__init__()
        self.title('FM2001 Clean-Room Prototype')
        self.geometry('1180x760')
        self.game_dir = Path(game_dir)
        self.db = FM2001Database(self.game_dir)
        self.gameplay = None
        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='FM2001 clean-room data prototype', font=('Segoe UI', 15, 'bold')).pack(side='left')
        ttk.Label(top, text=str(self.db.summary())).pack(side='right')
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self._clubs(nb)
        self._players(nb)
        self._managers(nb)
        self._play(nb)
        self._status(nb)

    def _clubs(self, nb):
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text='Clubs')
        q = tk.StringVar()
        ttk.Entry(f, textvariable=q).pack(fill='x', pady=(0, 8))
        tree = ttk.Treeview(f, columns=('id', 'name', 'short', 'stadium', 'manager'), show='headings')
        for col, title, width in [('id','ID',60),('name','Club',260),('short','Short',180),('stadium','Stadium',250),('manager','Manager',250)]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor='w')
        tree.pack(fill='both', expand=True)

        def fill(*_):
            term = q.get().strip().lower()
            tree.delete(*tree.get_children())
            for c in self.db.clubs:
                mgr = self.db.managers[c.manager_id].full_name if 0 <= c.manager_id < len(self.db.managers) else ''
                if term and term not in c.name.lower() and term not in c.stadium.lower() and term not in mgr.lower():
                    continue
                tree.insert('', 'end', values=(c.index, c.name, c.short_name, c.stadium, mgr))

        q.trace_add('write', fill)
        fill()

    def _position(self, code: int) -> str:
        pid = code + 1
        for p in self.db.positions:
            if p.id == pid:
                return p.abbreviation
        return str(code)

    def _players(self, nb):
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text='Players')
        pan = ttk.Panedwindow(f, orient='horizontal')
        pan.pack(fill='both', expand=True)
        left = ttk.Frame(pan)
        right = ttk.Frame(pan, padding=(12, 0, 0, 0))
        pan.add(left, weight=3)
        pan.add(right, weight=2)

        q = tk.StringVar()
        ttk.Entry(left, textvariable=q).pack(fill='x', pady=(0, 8))
        tree = ttk.Treeview(left, columns=('id','name','club','dob','pos'), show='headings', selectmode='browse')
        for col, title, width in [('id','ID',60),('name','Player',240),('club','Club',220),('dob','DOB',100),('pos','Pos',80)]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor='w')
        tree.pack(fill='both', expand=True)

        detail = tk.Text(right, wrap='word', font=('Consolas', 10), state='disabled')
        detail.pack(fill='both', expand=True)

        def fill(*_):
            term = q.get().strip().lower()
            tree.delete(*tree.get_children())
            for p in self.db.players:
                club = self.db.clubs[p.club_id].name if 0 <= p.club_id < len(self.db.clubs) else ''
                if term and term not in p.full_name.lower() and term not in club.lower():
                    continue
                tree.insert('', 'end', iid=str(p.index), values=(p.index, p.full_name, club, p.date_of_birth or '?', self._position(p.positions[0])))

        def select(_=None):
            sel = tree.selection()
            if not sel:
                return
            p = self.db.players[int(sel[0])]
            club = self.db.clubs[p.club_id].name if 0 <= p.club_id < len(self.db.clubs) else '?'
            cur = p.current
            target = p.target
            lines = [
                p.full_name,
                '=' * len(p.full_name),
                f'Club: {club}',
                f'DOB: {p.date_of_birth}',
                f'Height/weight: {p.height_cm} cm / {p.weight_kg} kg',
                f'Positions: {" / ".join(self._position(x) for x in p.positions)}',
                '',
                'Skill                 Current  Target',
                '-------------------------------------',
            ]
            for s in PLAYER_SKILLS:
                lines.append(f'{s:22} {cur[s]:>3}      {target[s]:>3}')
            detail.configure(state='normal')
            detail.delete('1.0', 'end')
            detail.insert('1.0', '\n'.join(lines))
            detail.configure(state='disabled')

        q.trace_add('write', fill)
        tree.bind('<<TreeviewSelect>>', select)
        fill()

    def _managers(self, nb):
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text='Managers')
        q = tk.StringVar()
        ttk.Entry(f, textvariable=q).pack(fill='x', pady=(0, 8))
        tree = ttk.Treeview(f, columns=('id','name','club','dob','joined'), show='headings')
        for col, title, width in [('id','ID',60),('name','Manager',250),('club','Club',240),('dob','DOB',100),('joined','Joined',100)]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor='w')
        tree.pack(fill='both', expand=True)

        def fill(*_):
            term = q.get().strip().lower()
            tree.delete(*tree.get_children())
            for m in self.db.managers:
                club = self.db.clubs[m.club_id].name if m.club_id is not None and 0 <= m.club_id < len(self.db.clubs) else ''
                if term and term not in m.full_name.lower() and term not in club.lower():
                    continue
                tree.insert('', 'end', values=(m.index, m.full_name, club, m.date_of_birth or '?', m.joined or '?'))

        q.trace_add('write', fill)
        fill()

    def _ensure_gameplay(self):
        if self.gameplay is None:
            self.gameplay = HumanGameplayController.from_canonical_game_dir(
                self.game_dir
            )
        return self.gameplay

    def _play(self, nb):
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text='Play')

        header = ttk.Frame(f)
        header.pack(fill='x', pady=(0, 8))
        ttk.Label(
            header,
            text='Minimum human-manager gameplay loop',
            font=('Segoe UI', 13, 'bold'),
        ).pack(side='left')
        status = tk.StringVar(value='Choose a Premier League club to begin.')
        ttk.Label(header, textvariable=status).pack(side='right')

        controls = ttk.Frame(f)
        controls.pack(fill='x', pady=(0, 8))

        pl_clubs = [
            club for club in self.db.clubs
            if int(getattr(club, 'competition_id', -1)) == 0
        ]
        club_values = [f'{club.index}: {club.name}' for club in pl_clubs]
        club_var = tk.StringVar(value=club_values[0] if club_values else '')
        ttk.Label(controls, text='Club').pack(side='left')
        club_box = ttk.Combobox(
            controls,
            textvariable=club_var,
            values=club_values,
            state='readonly',
            width=30,
        )
        club_box.pack(side='left', padx=(4, 8))

        formation_var = tk.IntVar(value=0)
        ttk.Label(controls, text='Formation').pack(side='left')
        ttk.Spinbox(
            controls,
            from_=0,
            to=20,
            textvariable=formation_var,
            width=4,
        ).pack(side='left', padx=(4, 8))

        play_style = tk.IntVar(value=1)
        without_ball = tk.IntVar(value=0)
        with_ball = tk.IntVar(value=0)
        aggression = tk.IntVar(value=5)
        for label, variable, maximum in (
            ('Play', play_style, 2),
            ('Without', without_ball, 3),
            ('With', with_ball, 3),
            ('Agg', aggression, 9),
        ):
            ttk.Label(controls, text=label).pack(side='left')
            ttk.Spinbox(
                controls,
                from_=0,
                to=maximum,
                textvariable=variable,
                width=3,
            ).pack(side='left', padx=(2, 6))

        body = ttk.Panedwindow(f, orient='horizontal')
        body.pack(fill='both', expand=True)
        left = ttk.Frame(body)
        right = ttk.Frame(body, padding=(10, 0, 0, 0))
        body.add(left, weight=3)
        body.add(right, weight=2)

        roster = ttk.Treeview(
            left,
            columns=('id', 'name', 'pos', 'condition', 'form', 'status'),
            show='headings',
            selectmode='extended',
        )
        for col, title, width in (
            ('id', 'ID', 60),
            ('name', 'Player', 210),
            ('pos', 'Pos', 70),
            ('condition', 'Cond', 60),
            ('form', 'Form', 55),
            ('status', 'Selection', 100),
        ):
            roster.heading(col, text=title)
            roster.column(col, width=width, anchor='w')
        roster.pack(fill='both', expand=True)

        selected_starters = set()
        selected_subs = set()

        table = ttk.Treeview(
            right,
            columns=('pos', 'club', 'p', 'w', 'd', 'l', 'gd', 'pts'),
            show='headings',
            height=16,
        )
        for col, title, width in (
            ('pos', '#', 35),
            ('club', 'Club', 150),
            ('p', 'P', 35),
            ('w', 'W', 35),
            ('d', 'D', 35),
            ('l', 'L', 35),
            ('gd', 'GD', 45),
            ('pts', 'Pts', 45),
        ):
            table.heading(col, text=title)
            table.column(col, width=width, anchor='w')
        table.pack(fill='both', expand=True)

        match_text = tk.StringVar(value='No fixture pending.')
        ttk.Label(right, textvariable=match_text, wraplength=390).pack(
            fill='x', pady=(8, 0)
        )

        def club_id_from_box():
            value = club_var.get().split(':', 1)[0].strip()
            if not value:
                raise ValueError('Select a Premier League club.')
            return int(value)

        def refresh_roster():
            roster.delete(*roster.get_children())
            if self.gameplay is None or self.gameplay.human is None:
                return
            for player in self.gameplay.squad():
                if player.index in selected_starters:
                    selection = 'XI'
                elif player.index in selected_subs:
                    selection = 'SUB'
                elif player.base_match_unavailable:
                    selection = 'Unavailable'
                else:
                    selection = ''
                roster.insert(
                    '',
                    'end',
                    iid=str(player.index),
                    values=(
                        player.index,
                        player.full_name,
                        self._position(player.current_position),
                        player.condition,
                        player.form_state,
                        selection,
                    ),
                )

        def refresh_table():
            table.delete(*table.get_children())
            if self.gameplay is None:
                return
            clubs = self.gameplay.state.clubs
            for position, row in enumerate(
                self.gameplay.state.premier_league_table(),
                start=1,
            ):
                club = clubs.get(int(row.club_id))
                club_name = (
                    getattr(club, 'name', str(row.club_id))
                    if club is not None
                    else str(row.club_id)
                )
                table.insert(
                    '',
                    'end',
                    values=(
                        position,
                        club_name,
                        row.played,
                        row.wins,
                        row.draws,
                        row.losses,
                        row.goal_difference,
                        row.points,
                    ),
                )

        def take_control():
            try:
                controller = self._ensure_gameplay()
                controller.select_club(club_id_from_box())
                selected_starters.clear()
                selected_subs.clear()
                status.set('Human club selected. Choose an XI and five substitutes.')
                refresh_roster()
                refresh_table()
            except Exception as exc:
                messagebox.showerror('FM2001 gameplay', str(exc))

        ttk.Button(
            controls,
            text='Take Control',
            command=take_control,
        ).pack(side='left', padx=(6, 0))

        line_buttons = ttk.Frame(left)
        line_buttons.pack(fill='x', pady=(6, 0))

        def set_xi():
            chosen = {int(value) for value in roster.selection()}
            if len(chosen) != 11:
                messagebox.showerror('FM2001 gameplay', 'Select exactly 11 XI players.')
                return
            if chosen & selected_subs:
                messagebox.showerror('FM2001 gameplay', 'XI and substitutes cannot overlap.')
                return
            selected_starters.clear()
            selected_starters.update(chosen)
            refresh_roster()

        def set_subs():
            chosen = {int(value) for value in roster.selection()}
            if len(chosen) != 5:
                messagebox.showerror('FM2001 gameplay', 'Select exactly 5 substitutes.')
                return
            if chosen & selected_starters:
                messagebox.showerror('FM2001 gameplay', 'XI and substitutes cannot overlap.')
                return
            selected_subs.clear()
            selected_subs.update(chosen)
            refresh_roster()

        def auto_fill():
            try:
                controller = self._ensure_gameplay()
                selection = controller.autofill_lineup(
                    int(formation_var.get())
                )
                selected_starters.clear()
                selected_subs.clear()
                selected_starters.update(
                    int(assignment.player_index)
                    for assignment in selection.lineup.starters
                )
                selected_subs.update(
                    int(player_id)
                    for player_id in selection.lineup.substitutes
                )
                status.set('Legal 11+5 lineup auto-filled.')
                refresh_roster()
            except Exception as exc:
                messagebox.showerror('FM2001 gameplay', str(exc))

        def apply_lineup():
            try:
                controller = self._ensure_gameplay()
                squad_order = tuple(
                    int(player.index)
                    for player in controller.squad()
                )
                controller.set_lineup(
                    int(formation_var.get()),
                    tuple(
                        player_id
                        for player_id in squad_order
                        if player_id in selected_starters
                    ),
                    tuple(
                        player_id
                        for player_id in squad_order
                        if player_id in selected_subs
                    ),
                )
                status.set('Lineup applied.')
                refresh_roster()
            except Exception as exc:
                messagebox.showerror('FM2001 gameplay', str(exc))

        def apply_tactics():
            try:
                controller = self._ensure_gameplay()
                controller.set_tactics(
                    TeamTacticalState(
                        play_style=int(play_style.get()),
                        without_ball_style=int(without_ball.get()),
                        with_ball_style=int(with_ball.get()),
                        aggression=int(aggression.get()),
                    )
                )
                status.set('Tactics applied.')
            except Exception as exc:
                messagebox.showerror('FM2001 gameplay', str(exc))

        for label, command in (
            ('Set XI', set_xi),
            ('Set Subs', set_subs),
            ('Auto Fill 11+5', auto_fill),
            ('Apply Lineup', apply_lineup),
            ('Apply Tactics', apply_tactics),
        ):
            ttk.Button(line_buttons, text=label, command=command).pack(
                side='left', padx=(0, 5)
            )

        progress = ttk.Frame(right)
        progress.pack(fill='x', pady=(8, 0))

        def advance_match():
            try:
                controller = self._ensure_gameplay()
                fixture = controller.advance_to_next_user_fixture()
                if fixture is None:
                    match_text.set('No remaining Premier League fixture.')
                    return
                clubs = controller.state.clubs
                home = clubs.get(int(fixture.home_club_id))
                away = clubs.get(int(fixture.away_club_id))
                home_name = getattr(home, 'name', str(fixture.home_club_id))
                away_name = getattr(away, 'name', str(fixture.away_club_id))
                match_text.set(
                    f'{controller.state.calendar.current_date}: '
                    f'{home_name} vs {away_name}. Ready to play.'
                )
                status.set('Advanced to the next human fixture.')
                refresh_table()
            except Exception as exc:
                messagebox.showerror('FM2001 gameplay', str(exc))

        def play_match():
            try:
                controller = self._ensure_gameplay()
                fixture = controller.state.premier_league.fixtures[
                    controller.pending_fixture_id
                ]
                outcome = controller.play_user_fixture()
                score = outcome.user_result.score
                clubs = controller.state.clubs
                home = clubs.get(int(fixture.home_club_id))
                away = clubs.get(int(fixture.away_club_id))
                home_name = getattr(home, 'name', str(fixture.home_club_id))
                away_name = getattr(away, 'name', str(fixture.away_club_id))
                match_text.set(
                    f'{home_name} {score[0]} - {score[1]} {away_name}. '
                    f'Matchday completed.'
                )
                status.set('Result stored. Adjust lineup or continue.')
                refresh_roster()
                refresh_table()
            except Exception as exc:
                messagebox.showerror('FM2001 gameplay', str(exc))

        ttk.Button(
            progress,
            text='Advance to Next Match',
            command=advance_match,
        ).pack(side='left', padx=(0, 6))
        ttk.Button(
            progress,
            text='Play Match',
            command=play_match,
        ).pack(side='left')

    def _status(self, nb):
        f = ttk.Frame(nb, padding=20)
        nb.add(f, text='Status')
        text = (
            'Clean-room prototype. Contains no EA game data or executable code.\n\n'
            'Reads the user\'s existing Master.dat, Core.str, English.str and Static.dat.\n\n'
            'Implemented here:\n'
            '• corrected 4-byte player-section header\n'
            '• 1,246 clubs, 30,064 players and 1,612 managers\n'
            '• current club links, DOB, physical data and positions\n'
            '• all 17 current skills and 17 development targets\n'
            '• exact FM2001 0..30 display conversion\n'
            '• manager identities / club links\n\n'
            'Gameplay now available in the Play tab:\n'
            '• choose a Premier League club\n'
            '• choose formation, XI, substitutes and tactics\n'
            '• advance through the recovered scheduler\n'
            '• simulate human-vs-AI matches through the shared backend\n'
            '• inspect results and the live league table\n\n'
            'Still outside this temporary surface:\n'
            '• full transfers/finances UI\n'
            '• save-game compatibility\n'
            '• faithful original UI / FastView'
        )
        ttk.Label(f, text=text, justify='left', font=('Segoe UI', 11)).pack(anchor='nw')

def choose_dir() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    p = filedialog.askdirectory(title='Select FM2001 game folder')
    root.destroy()
    return Path(p) if p else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game_dir', nargs='?', default=str(DEFAULT_GAME_DIR))
    args = ap.parse_args()
    game_dir = Path(args.game_dir)
    if not (game_dir / 'Master.dat').exists():
        game_dir = choose_dir()
        if game_dir is None:
            return
    try:
        App(game_dir).mainloop()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('FM2001 prototype', str(exc))
        root.destroy()
        raise

if __name__ == '__main__':
    main()
