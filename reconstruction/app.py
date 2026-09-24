from __future__ import annotations
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from fm2001_data import FM2001Database, PLAYER_SKILLS

DEFAULT_GAME_DIR = Path(r'C:\Games\FM2001')

class App(tk.Tk):
    def __init__(self, game_dir: Path):
        super().__init__()
        self.title('FM2001 Clean-Room Prototype')
        self.geometry('1180x760')
        self.db = FM2001Database(game_dir)
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
            'Not yet implemented as gameplay:\n'
            '• season simulation and AI\n'
            '• full transfers/finances UI\n'
            '• save-game compatibility\n'
            '• match engine / FastView'
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
