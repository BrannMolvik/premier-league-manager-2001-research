"""Explicit temporary playtest, not the original-style production host.

Uses the existing verified controller and internal saves. Generic widgets and
autofill are development conveniences, never native UI/fidelity evidence.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from queue import Queue, Empty
from threading import Thread

from gate13_management_source_data import ManagementSourceDataBridge
from human_gameplay import HumanGameplayController
from internal_save import load_human_gameplay, save_human_gameplay
from match_team_setup import resolved_substitute_quota


class DevelopmentPlaytestSession:
    def __init__(self, controller, database):
        self.controller = controller
        self.database = database

    @classmethod
    def open(cls, game_dir):
        from fm2001_data import FM2001Database
        from verify import verify_canonical_files
        verify_canonical_files(game_dir)
        database = FM2001Database(game_dir)
        return cls(HumanGameplayController.from_verified_canonical_database(game_dir, database), database)

    def clubs(self):
        c = self.controller
        return tuple((club_id, c.state.clubs[club_id].name)
                     for club_id in c.selectable_club_ids())

    def select(self, club_id):
        return self.controller.select_club(club_id)

    def roster(self):
        # Full retained source order, not the ordinary host's initial 20 shells.
        return ManagementSourceDataBridge(self.controller).squad_rows()

    def table(self):
        # Deliberately uses the controlled club's actual live League owner.
        return self.controller._human_live_league_table()

    def pending_names(self):
        c = self.controller
        if c.pending_primary_entry is None:
            return None
        pair = c._primary_entry_clubs(c.pending_primary_entry)
        if pair is None:
            raise RuntimeError('Pending native match has no resolved participants.')
        return tuple(c.state.clubs[club_id].name for club_id in pair)

    def substitute_quota(self):
        return resolved_substitute_quota(
            int(self.controller._human_selection_competition().substitute_quota))

    def advance(self):
        return self.controller.advance_to_next_user_primary_match()

    def play(self):
        return self.controller.play_user_primary_match()

    def save(self, path):
        if self.controller.human is None:
            raise RuntimeError('Select a club before saving.')
        save_human_gameplay(self.controller, path)

    def load(self, path):
        c = self.controller
        loaded = load_human_gameplay(self.database, c.attack_matrix, c.defence_matrix, path)
        self.controller = loaded


def run(game_dir):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from windows_display_context import initialize_windows_display_context

    initialize_windows_display_context()
    root = tk.Tk()
    root.title('FM2001 DEVELOPMENT PLAYTEST — not original UI / not final release')
    root.geometry('1100x760')
    ttk.Label(root, text='Temporary development fallback — original UI remains unfinished',
              font=('Segoe UI', 13, 'bold')).pack(pady=8)
    status = tk.StringVar(value='Loading verified original data...')
    ttk.Label(root, textvariable=status, wraplength=1050).pack(pady=3)
    root.update()
    session = DevelopmentPlaytestSession.open(game_dir)
    controls = ttk.Frame(root, padding=8)
    controls.pack(fill='x')
    choices = [f'{cid}: {name}' for cid, name in session.clubs()]
    preferred = next((v for v in choices if v.endswith(': Southport')), choices[0])
    club = tk.StringVar(value=preferred)
    club_box = ttk.Combobox(controls, textvariable=club, values=choices,
                           state='readonly', width=28)
    club_box.pack(side='left', padx=4)
    formation = tk.IntVar(value=0)
    ttk.Label(controls, text='Formation ID').pack(side='left', padx=4)
    spin = ttk.Spinbox(controls, from_=0, to=20, textvariable=formation, width=4)
    spin.pack(side='left')
    body = ttk.Panedwindow(root, orient='horizontal')
    body.pack(fill='both', expand=True, padx=8)
    left, right = ttk.Frame(body), ttk.Frame(body)
    body.add(left, weight=1)
    body.add(right, weight=1)
    roster = ttk.Treeview(left, columns=('name', 'role', 'cond', 'form', 'lineup'),
                         show='headings', selectmode='extended')
    for col, title, width in (('name','Player',180), ('role','Role',55),
                              ('cond','Cond',45), ('form','Form',45), ('lineup','XI/Bench',70)):
        roster.heading(col, text=title)
        roster.column(col, width=width, stretch=col == 'name')
    scrollbar = ttk.Scrollbar(left, orient='vertical', command=roster.yview)
    scrollbar.pack(side='right', fill='y')
    roster.configure(yscrollcommand=scrollbar.set)
    roster.pack(fill='both', expand=True)
    table = ttk.Treeview(right, columns=('club','p','w','d','l','f','a','pts'), show='headings')
    for col in ('club','p','w','d','l','f','a','pts'):
        table.heading(col, text=col.upper())
        table.column(col, width=175 if col == 'club' else 36, stretch=col == 'club')
    table.pack(fill='both', expand=True)
    buttons = ttk.Frame(root, padding=8)
    buttons.pack(fill='x')
    result = tk.StringVar(value='Select a club, autofill or select XI/bench, then advance and play.')
    ttk.Label(root, textvariable=result, wraplength=1050).pack(pady=(0,8))
    starters, subs = set(), set()
    queue, busy, widgets = Queue(), [False], [club_box, spin]

    def refresh():
        c = session.controller
        if c.human is None:
            status.set('No active human club. Select one to start.')
            return
        roster.delete(*roster.get_children())
        for row in session.roster():
            tag = 'XI' if row.player_id in starters else 'Bench' if row.player_id in subs else ''
            roster.insert('', 'end', iid=str(row.player_id), values=(row.full_name,
                row.assigned_role_abbreviation, row.condition, row.recent_form_average, tag))
        table.delete(*table.get_children())
        for row in session.table():
            table.insert('', 'end', values=(c.state.clubs[row.club_id].name, row.played,
                row.wins, row.draws, row.losses, row.goals_for, row.goals_against, row.points))
        status.set(f'{c.state.clubs[c.human.club_id].name} — {c.state.calendar.current_date} — '
                   f'{len(roster.get_children())} players — bench quota {session.substitute_quota()}')

    def sync():
        c = session.controller
        starters.clear()
        subs.clear()
        if c.human is not None:
            starters.update(c.human.starter_ids)
            subs.update(c.human.substitute_ids)
            formation.set(c.human.formation_id)
            club.set(f'{c.human.club_id}: {c.state.clubs[c.human.club_id].name}')
        refresh()

    def guarded(fn):
        if busy[0]:
            return
        try:
            fn()
        except Exception as exc:
            messagebox.showerror('Development playtest — operation failed', str(exc), parent=root)

    def select():
        session.select(int(club.get().split(':',1)[0]))
        sync()

    def autofill():
        session.controller.autofill_lineup(formation.get())
        sync()

    def set_selected(target, other, required):
        chosen = {int(v) for v in roster.selection()}
        if len(chosen) != required or chosen & other:
            raise ValueError(f'Select exactly {required} players without XI/bench overlap.')
        target.clear()
        target.update(chosen)
        refresh()

    def apply():
        order = [row.player_id for row in session.roster()]
        session.controller.set_lineup(formation.get(), tuple(v for v in order if v in starters),
                                      tuple(v for v in order if v in subs))
        sync()

    def async_action(action, done):
        busy[0] = True
        for widget in widgets:
            widget.configure(state='disabled')
        result.set('Working through the existing scheduler/calculator; please wait...')
        def worker():
            try:
                queue.put((done, action(), None))
            except Exception as exc:
                queue.put((done, None, exc))
        Thread(target=worker, daemon=True).start()

    def poll():
        try:
            done, value, error = queue.get_nowait()
        except Empty:
            root.after(50, poll)
            return
        busy[0] = False
        for widget in widgets:
            widget.configure(state='readonly' if widget is club_box else 'normal')
        if error:
            result.set(f'Operation failed: {error}. State is not replaced with a guessed result.')
            messagebox.showerror('Development playtest', str(error), parent=root)
        else:
            guarded(lambda: done(value))
        root.after(50, poll)

    def advanced(entry):
        names = session.pending_names()
        result.set('No remaining scheduled human match.' if entry is None else
                   f'{names[0]} vs {names[1]} — ready. Check lineup then Play.')
        refresh()

    def play():
        names = session.pending_names()
        if names is None:
            raise RuntimeError('Advance to a match first.')
        def done(outcome):
            score = outcome.user_result.score
            result.set(f'{names[0]} {score[0]} - {score[1]} {names[1]} — completed. Save or advance.')
            sync()
        async_action(session.play, done)

    def save():
        path = filedialog.asksaveasfilename(parent=root, defaultextension='.fm2k',
                initialfile='train-playtest.fm2k', filetypes=[('Internal FM2001 port save','*.fm2k')])
        if path:
            session.save(path)
            result.set(f'Saved {path}')

    def load():
        path = filedialog.askopenfilename(parent=root, filetypes=[('Internal FM2001 port save','*.fm2k')])
        if path:
            session.load(path)
            sync()
            result.set(f'Loaded {path}; pending match: {session.pending_names()}')

    for label, command in (
        ('Take Control', select), ('Auto Fill', autofill),
        ('Set XI', lambda: set_selected(starters, subs, 11)),
        ('Set Bench', lambda: set_selected(subs, starters, session.substitute_quota())),
        ('Apply Lineup', apply), ('Advance', lambda: async_action(session.advance, advanced)),
        ('Play', play), ('Save', save), ('Load', load)):
        button = ttk.Button(buttons, text=label, command=lambda fn=command: guarded(fn))
        button.pack(side='left', padx=2)
        widgets.append(button)
    root.after(50, poll)
    status.set('Verified original data loaded. Temporary generic UI; not Gate-13 closure.')
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_dir', type=Path, nargs='?', default=Path(r'C:\Games\FM2001'))
    run(parser.parse_args().game_dir)
