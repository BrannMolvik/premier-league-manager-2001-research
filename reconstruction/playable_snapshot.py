from __future__ import annotations

import argparse
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from fm2001_data import FM2001Database
from human_gameplay import HumanGameplayController
from internal_save import load_human_gameplay, save_human_gameplay
from match_team_setup import TeamTacticalState
from player_development import TRAINING_METHOD_NAMES
from scouting import ScoutingReseedState
from transfer_state import ContractTerms

DEFAULT_GAME_DIR = Path(r"C:\Games\FM2001")


class CurrentPlayableSnapshot(tk.Tk):
    """Temporary Gate-12 playable shell over the reconstructed FM2001 backend.

    This deliberately does not pretend to be Gate-13 presentation fidelity.
    It exposes source-backed gameplay that already exists in the reconstruction
    while the main reverse-engineering worker continues independently.
    """

    def __init__(self, game_dir: Path):
        super().__init__()
        self.title("FM2001 Windows 11 Port - Current Playable Snapshot")
        self.geometry("1360x860")
        self.minsize(1120, 720)

        self.game_dir = Path(game_dir)
        self.db = FM2001Database(self.game_dir)
        self.gameplay: HumanGameplayController | None = None

        self.selected_starters: set[int] = set()
        self.selected_subs: set[int] = set()
        self.scouting_results: list[object] = []

        self.club_var = tk.StringVar()
        self.date_var = tk.StringVar(value="No game started")
        self.status_var = tk.StringVar(
            value="Choose a Premier League club on Home to start."
        )
        self.match_var = tk.StringVar(value="No match pending.")

        self._build()
        self._refresh_all()

    # ---------- generic helpers ----------

    def _club_name(self, club_id: int) -> str:
        club = None
        if self.gameplay is not None:
            club = self.gameplay.state.clubs.get(int(club_id))
        if club is None and 0 <= int(club_id) < len(self.db.clubs):
            club = self.db.clubs[int(club_id)]
        return str(getattr(club, "name", club_id))

    def _position_name(self, code: int) -> str:
        pid = int(code) + 1
        for pos in self.db.positions:
            if int(getattr(pos, "id", -1)) == pid:
                return str(getattr(pos, "abbreviation", code))
        return str(code)

    def _require_game(self) -> HumanGameplayController:
        if self.gameplay is None or self.gameplay.human is None:
            raise RuntimeError("Choose a club on Home first.")
        return self.gameplay

    def _show_error(self, title: str, exc: Exception):
        messagebox.showerror(title, str(exc))

    def _ensure_gameplay(self) -> HumanGameplayController:
        if self.gameplay is None:
            self.status_var.set("Loading canonical FM2001 runtime...")
            self.update_idletasks()
            self.gameplay = HumanGameplayController.from_canonical_game_dir(
                self.game_dir
            )
        return self.gameplay

    def _human_club_id(self) -> int | None:
        if self.gameplay is None or self.gameplay.human is None:
            return None
        return int(self.gameplay.human.club_id)

    # ---------- shell ----------

    def _build(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill="x")
        ttk.Label(
            header,
            text="The F.A. Premier League Football Manager 2001",
            font=("Segoe UI", 17, "bold"),
        ).pack(side="left")
        ttk.Label(
            header,
            text="Gate-12 playable snapshot",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(12, 0))
        ttk.Label(header, textvariable=self.date_var).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self._build_home()
        self._build_squad()
        self._build_matchday()
        self._build_scouting()
        self._build_youth()
        self._build_finances()
        self._build_inbox()
        self._build_status()

        footer = ttk.Frame(self, padding=(12, 6))
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left")
        ttk.Button(footer, text="Save", command=self._save_game).pack(
            side="right", padx=(6, 0)
        )
        ttk.Button(footer, text="Load", command=self._load_game).pack(side="right")

    # ---------- home ----------

    def _build_home(self):
        frame = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(frame, text="Home")

        ttk.Label(
            frame,
            text="Current playable reconstruction",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                "This snapshot exposes the reconstructed management backend as it "
                "exists now. It is intentionally a temporary management shell, not "
                "the later original FM2001 presentation restoration."
            ),
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(4, 14))

        select = ttk.LabelFrame(frame, text="Manager setup", padding=10)
        select.pack(fill="x")

        clubs = [
            club for club in self.db.clubs
            if int(getattr(club, "competition_id", -1)) == 0
        ]
        self.club_values = [f"{club.index}: {club.name}" for club in clubs]
        if self.club_values:
            self.club_var.set(self.club_values[0])

        ttk.Label(select, text="Premier League club").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            select,
            textvariable=self.club_var,
            values=self.club_values,
            state="readonly",
            width=36,
        ).grid(row=0, column=1, sticky="w", padx=(8, 8))
        ttk.Button(
            select,
            text="Take Control / New Game",
            command=self._take_control,
        ).grid(row=0, column=2, sticky="w")

        self.home_summary = tk.Text(
            frame, height=20, wrap="word", font=("Consolas", 10), state="disabled"
        )
        self.home_summary.pack(fill="both", expand=True, pady=(14, 0))

    def _take_control(self):
        try:
            value = self.club_var.get().split(":", 1)[0].strip()
            if not value:
                raise ValueError("Choose a Premier League club.")
            controller = self._ensure_gameplay()
            controller.select_club(int(value))
            self.selected_starters.clear()
            self.selected_subs.clear()
            self._autofill_lineup(apply_immediately=True)
            self.status_var.set(
                f"Managing {self._club_name(controller.human.club_id)}."
            )
            self._refresh_all()
        except Exception as exc:
            self._show_error("Start game", exc)

    # ---------- squad / training ----------

    def _build_squad(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Squad & Training")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="Training method").pack(side="left")
        self.training_var = tk.StringVar(value=TRAINING_METHOD_NAMES[0])
        ttk.Combobox(
            controls,
            textvariable=self.training_var,
            values=TRAINING_METHOD_NAMES,
            state="readonly",
            width=23,
        ).pack(side="left", padx=(6, 6))
        ttk.Button(
            controls,
            text="Assign to selected player",
            command=self._assign_training,
        ).pack(side="left")

        self.squad_tree = ttk.Treeview(
            frame,
            columns=(
                "id", "player", "pos", "age", "cond", "morale", "form",
                "wage", "contract", "training", "status"
            ),
            show="headings",
            selectmode="browse",
        )
        headings = (
            ("id", "ID", 55),
            ("player", "Player", 210),
            ("pos", "Pos", 60),
            ("age", "Age", 45),
            ("cond", "Cond", 50),
            ("morale", "Morale", 55),
            ("form", "Form", 45),
            ("wage", "Weekly wage", 90),
            ("contract", "Contract", 95),
            ("training", "Training", 120),
            ("status", "Status", 130),
        )
        for col, title, width in headings:
            self.squad_tree.heading(col, text=title)
            self.squad_tree.column(col, width=width, anchor="w")
        self.squad_tree.pack(fill="both", expand=True)

    def _assign_training(self):
        try:
            controller = self._require_game()
            sel = self.squad_tree.selection()
            if not sel:
                raise RuntimeError("Select one squad player.")
            player_id = int(sel[0])
            method_id = TRAINING_METHOD_NAMES.index(self.training_var.get())
            controller.set_player_training_method(player_id, method_id)
            self.status_var.set(
                f"Training set to {TRAINING_METHOD_NAMES[method_id]}."
            )
            self._refresh_squad()
        except Exception as exc:
            self._show_error("Training", exc)

    def _refresh_squad(self):
        if not hasattr(self, "squad_tree"):
            return
        self.squad_tree.delete(*self.squad_tree.get_children())
        if self.gameplay is None or self.gameplay.human is None:
            return
        on_date = self.gameplay.state.calendar.current_date
        for player in self.gameplay.squad():
            status = []
            if player.injured:
                status.append("Injured")
            if player.suspended:
                status.append("Suspended")
            if player.transfer_listed:
                status.append("Transfer listed")
            if player.loan_listed:
                status.append("Loan listed")
            if player.out_of_contract:
                status.append("Out of contract")
            age = player.age(on_date)
            contract = (
                player.contract_expiry_date.isoformat()
                if player.contract_expiry_date is not None else ""
            )
            method = (
                TRAINING_METHOD_NAMES[int(player.training_method_id)]
                if 0 <= int(player.training_method_id) < len(TRAINING_METHOD_NAMES)
                else str(player.training_method_id)
            )
            self.squad_tree.insert(
                "",
                "end",
                iid=str(player.index),
                values=(
                    player.index,
                    player.full_name,
                    self._position_name(player.current_position),
                    "" if age is None else age,
                    player.condition,
                    player.morale,
                    player.form_state,
                    player.weekly_wage,
                    contract,
                    method,
                    ", ".join(status),
                ),
            )

    # ---------- matchday ----------

    def _build_matchday(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Matchday")

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 8))

        self.formation_var = tk.IntVar(value=0)
        self.play_style_var = tk.IntVar(value=1)
        self.without_ball_var = tk.IntVar(value=0)
        self.with_ball_var = tk.IntVar(value=0)
        self.aggression_var = tk.IntVar(value=5)

        for label, variable, maximum in (
            ("Formation", self.formation_var, 20),
            ("Play", self.play_style_var, 2),
            ("Without", self.without_ball_var, 3),
            ("With", self.with_ball_var, 3),
            ("Aggression", self.aggression_var, 9),
        ):
            ttk.Label(top, text=label).pack(side="left")
            ttk.Spinbox(
                top, from_=0, to=maximum, textvariable=variable, width=4
            ).pack(side="left", padx=(3, 8))

        ttk.Button(
            top, text="Auto-fill 11+5", command=self._autofill_lineup
        ).pack(side="left", padx=(4, 4))
        ttk.Button(
            top, text="Apply selected XI", command=self._set_selected_xi
        ).pack(side="left", padx=(0, 4))
        ttk.Button(
            top, text="Apply selected subs", command=self._set_selected_subs
        ).pack(side="left", padx=(0, 4))
        ttk.Button(
            top, text="Apply lineup/tactics", command=self._apply_lineup_and_tactics
        ).pack(side="left")

        body = ttk.Panedwindow(frame, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body)
        right = ttk.Frame(body, padding=(10, 0, 0, 0))
        body.add(left, weight=3)
        body.add(right, weight=2)

        self.lineup_tree = ttk.Treeview(
            left,
            columns=("player", "pos", "condition", "morale", "selection"),
            show="headings",
            selectmode="extended",
        )
        for col, title, width in (
            ("player", "Player", 210),
            ("pos", "Pos", 60),
            ("condition", "Cond", 55),
            ("morale", "Morale", 60),
            ("selection", "Selection", 100),
        ):
            self.lineup_tree.heading(col, text=title)
            self.lineup_tree.column(col, width=width, anchor="w")
        self.lineup_tree.pack(fill="both", expand=True)

        ttk.Label(
            right, textvariable=self.match_var, wraplength=420, justify="left"
        ).pack(fill="x", pady=(0, 8))

        actions = ttk.Frame(right)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(
            actions,
            text="Advance to next match",
            command=self._advance_to_match,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            actions,
            text="Play match",
            command=self._play_match,
        ).pack(side="left")

        self.table_tree = ttk.Treeview(
            right,
            columns=("pos", "club", "p", "w", "d", "l", "gd", "pts"),
            show="headings",
            height=18,
        )
        for col, title, width in (
            ("pos", "#", 32),
            ("club", "Club", 145),
            ("p", "P", 32),
            ("w", "W", 32),
            ("d", "D", 32),
            ("l", "L", 32),
            ("gd", "GD", 42),
            ("pts", "Pts", 42),
        ):
            self.table_tree.heading(col, text=title)
            self.table_tree.column(col, width=width, anchor="w")
        self.table_tree.pack(fill="both", expand=True)

        self.match_log = tk.Text(
            right, height=8, wrap="word", font=("Consolas", 9), state="disabled"
        )
        self.match_log.pack(fill="x", pady=(8, 0))

    def _autofill_lineup(self, apply_immediately: bool = False):
        try:
            controller = self._require_game()
            selection = controller.autofill_lineup(int(self.formation_var.get()))
            self.selected_starters = {
                int(x.player_index) for x in selection.lineup.starters
            }
            self.selected_subs = {
                int(x) for x in selection.lineup.substitutes
            }
            if apply_immediately:
                controller.set_lineup(
                    int(self.formation_var.get()),
                    tuple(
                        int(x.player_index)
                        for x in selection.lineup.starters
                    ),
                    tuple(int(x) for x in selection.lineup.substitutes),
                )
            self._refresh_lineup()
            self.status_var.set("Legal 11+5 lineup auto-filled.")
        except Exception as exc:
            if apply_immediately:
                raise
            self._show_error("Lineup", exc)

    def _set_selected_xi(self):
        try:
            chosen = {int(x) for x in self.lineup_tree.selection()}
            if len(chosen) != 11:
                raise ValueError("Select exactly 11 players.")
            if chosen & self.selected_subs:
                raise ValueError("XI and substitutes cannot overlap.")
            self.selected_starters = chosen
            self._refresh_lineup()
        except Exception as exc:
            self._show_error("Lineup", exc)

    def _set_selected_subs(self):
        try:
            chosen = {int(x) for x in self.lineup_tree.selection()}
            if len(chosen) != 5:
                raise ValueError("Select exactly 5 substitutes.")
            if chosen & self.selected_starters:
                raise ValueError("XI and substitutes cannot overlap.")
            self.selected_subs = chosen
            self._refresh_lineup()
        except Exception as exc:
            self._show_error("Lineup", exc)

    def _apply_lineup_and_tactics(self):
        try:
            controller = self._require_game()
            squad_order = tuple(int(p.index) for p in controller.squad())
            controller.set_lineup(
                int(self.formation_var.get()),
                tuple(x for x in squad_order if x in self.selected_starters),
                tuple(x for x in squad_order if x in self.selected_subs),
            )
            controller.set_tactics(
                TeamTacticalState(
                    play_style=int(self.play_style_var.get()),
                    without_ball_style=int(self.without_ball_var.get()),
                    with_ball_style=int(self.with_ball_var.get()),
                    aggression=int(self.aggression_var.get()),
                )
            )
            self.status_var.set("Lineup and tactics applied.")
            self._refresh_lineup()
        except Exception as exc:
            self._show_error("Match setup", exc)

    def _entry_description(self, entry: tuple | None) -> str:
        if entry is None:
            return "No match pending."
        controller = self._require_game()
        pair = controller._primary_entry_clubs(tuple(entry))
        if pair is None:
            return repr(entry)
        home, away = pair
        if entry[0] == "premier_league":
            comp = "Premier League"
        else:
            token = tuple(entry[1])
            comp_id = int(token[1]) if len(token) > 1 else -1
            competition = controller.state.competitions.get(comp_id)
            comp = str(getattr(competition, "name", f"Cup {comp_id}"))
        return (
            f"{controller.state.calendar.current_date.isoformat()} | {comp}: "
            f"{self._club_name(home)} vs {self._club_name(away)}"
        )

    def _advance_to_match(self):
        try:
            controller = self._require_game()
            self._apply_lineup_and_tactics()
            entry = controller.advance_to_next_user_primary_match()
            if entry is None:
                self.match_var.set("No remaining supported first-team match.")
                self.status_var.set("No remaining supported match found.")
            else:
                self.match_var.set(self._entry_description(tuple(entry)))
                self.status_var.set("Advanced to the next user match.")
            self._refresh_all()
        except Exception as exc:
            self._show_error("Advance", exc)

    def _play_match(self):
        try:
            controller = self._require_game()
            if controller.pending_primary_entry is None:
                raise RuntimeError("Advance to a match first.")
            description = self._entry_description(
                tuple(controller.pending_primary_entry)
            )
            outcome = controller.play_user_primary_match()
            score = getattr(outcome.user_result, "score", None)
            if score is None:
                score_text = str(outcome.user_result)
            else:
                score_text = f"{score[0]}-{score[1]}"
            self._append_match_log(f"{description}\nResult: {score_text}\n")
            self.match_var.set(f"Last result: {score_text}")
            self.status_var.set("Match completed and shared matchday finalized.")
            self._refresh_all()
        except Exception as exc:
            self._show_error("Play match", exc)

    def _append_match_log(self, text: str):
        self.match_log.configure(state="normal")
        self.match_log.insert("end", text + "\n")
        self.match_log.see("end")
        self.match_log.configure(state="disabled")

    def _refresh_lineup(self):
        if not hasattr(self, "lineup_tree"):
            return
        self.lineup_tree.delete(*self.lineup_tree.get_children())
        if self.gameplay is None or self.gameplay.human is None:
            return
        for player in self.gameplay.squad():
            if int(player.index) in self.selected_starters:
                selection = "XI"
            elif int(player.index) in self.selected_subs:
                selection = "SUB"
            elif player.base_match_unavailable:
                selection = "Unavailable"
            else:
                selection = ""
            self.lineup_tree.insert(
                "",
                "end",
                iid=str(player.index),
                values=(
                    player.full_name,
                    self._position_name(player.current_position),
                    player.condition,
                    player.morale,
                    selection,
                ),
            )

    def _refresh_table(self):
        if not hasattr(self, "table_tree"):
            return
        self.table_tree.delete(*self.table_tree.get_children())
        if self.gameplay is None:
            return
        for position, row in enumerate(
            self.gameplay.state.premier_league_table(), start=1
        ):
            self.table_tree.insert(
                "",
                "end",
                values=(
                    position,
                    self._club_name(int(row.club_id)),
                    row.played,
                    row.wins,
                    row.draws,
                    row.losses,
                    row.goal_difference,
                    row.points,
                ),
            )

    # ---------- scouting / transfers ----------

    def _build_scouting(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Scouting & Transfers")

        search = ttk.Frame(frame)
        search.pack(fill="x", pady=(0, 8))
        self.scout_query = tk.StringVar()
        ttk.Label(search, text="Player search").pack(side="left")
        ttk.Entry(search, textvariable=self.scout_query, width=34).pack(
            side="left", padx=(6, 6)
        )
        ttk.Button(search, text="Scout", command=self._run_scouting).pack(side="left")

        body = ttk.Panedwindow(frame, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        right = ttk.Frame(body, padding=(10, 0, 0, 0))
        body.add(left, weight=3)
        body.add(right, weight=2)

        self.scout_tree = ttk.Treeview(
            left,
            columns=("id", "player", "club", "age", "pos", "wage", "status"),
            show="headings",
            selectmode="browse",
        )
        for col, title, width in (
            ("id", "ID", 55),
            ("player", "Player", 190),
            ("club", "Club", 160),
            ("age", "Age", 45),
            ("pos", "Pos", 55),
            ("wage", "Wage", 70),
            ("status", "Status", 120),
        ):
            self.scout_tree.heading(col, text=title)
            self.scout_tree.column(col, width=width, anchor="w")
        self.scout_tree.pack(fill="both", expand=True)

        bid = ttk.LabelFrame(right, text="Cash bid", padding=8)
        bid.pack(fill="x")
        self.bid_fee = tk.IntVar(value=1_000_000)
        ttk.Label(bid, text="Fee").grid(row=0, column=0, sticky="w")
        ttk.Entry(bid, textvariable=self.bid_fee, width=16).grid(
            row=0, column=1, sticky="w", padx=(6, 6)
        )
        ttk.Button(bid, text="Submit bid", command=self._submit_bid).grid(
            row=0, column=2
        )

        contract = ttk.LabelFrame(right, text="Contract offer", padding=8)
        contract.pack(fill="x", pady=(8, 0))
        self.contract_wage = tk.IntVar(value=10_000)
        self.contract_signing = tk.IntVar(value=50_000)
        self.contract_months = tk.IntVar(value=36)
        self.contract_appearance = tk.IntVar(value=0)
        fields = (
            ("Weekly wage", self.contract_wage),
            ("Signing fee", self.contract_signing),
            ("Months", self.contract_months),
            ("Appearance fee", self.contract_appearance),
        )
        for row, (label, variable) in enumerate(fields):
            ttk.Label(contract, text=label).grid(row=row, column=0, sticky="w")
            ttk.Entry(contract, textvariable=variable, width=16).grid(
                row=row, column=1, sticky="w", padx=(6, 0), pady=2
            )
        ttk.Button(
            contract, text="Offer contract", command=self._offer_contract
        ).grid(row=len(fields), column=0, columnspan=2, sticky="w", pady=(6, 0))

        ttk.Button(
            right,
            text="Process transfers due today",
            command=self._process_transfers,
        ).pack(anchor="w", pady=(10, 0))

        self.transfer_output = tk.Text(
            right, height=15, wrap="word", font=("Consolas", 9), state="disabled"
        )
        self.transfer_output.pack(fill="both", expand=True, pady=(8, 0))

    def _run_scouting(self):
        try:
            controller = self._require_game()
            term = self.scout_query.get().strip().lower()

            def predicate(player):
                club_name = self._club_name(int(player.club_id)).lower()
                return (
                    not term
                    or term in player.full_name.lower()
                    or term in club_name
                )

            results = controller.search_scouting_players(
                ScoutingReseedState(),
                candidate_predicate=predicate,
                sort_mode=0,
            )
            self.scouting_results = list(results)
            self._refresh_scout_results()
            self.status_var.set(
                f"Scouting returned {len(self.scouting_results)} result(s)."
            )
        except Exception as exc:
            self._show_error("Scouting", exc)

    def _selected_scout_player(self):
        sel = self.scout_tree.selection()
        if not sel:
            raise RuntimeError("Select a scouted player.")
        controller = self._require_game()
        player = controller.state.players.get(int(sel[0]))
        if player is None:
            raise RuntimeError("Selected player is no longer available.")
        return player

    def _submit_bid(self):
        try:
            controller = self._require_game()
            player = self._selected_scout_player()
            result = controller.submit_cash_bid(player.index, int(self.bid_fee.get()))
            self._write_transfer_output(
                f"Bid for {player.full_name}: {result!r}\n"
            )
            self.status_var.set("Cash bid evaluated.")
            self._refresh_finances()
        except Exception as exc:
            self._show_error("Transfer bid", exc)

    def _offer_contract(self):
        try:
            controller = self._require_game()
            player = self._selected_scout_player()
            terms = ContractTerms(
                weekly_wage=int(self.contract_wage.get()),
                signing_on_fee=int(self.contract_signing.get()),
                contract_length_months=int(self.contract_months.get()),
                appearance_fee=int(self.contract_appearance.get()),
            )
            result = controller.offer_player_contract(player.index, terms)
            self._write_transfer_output(
                f"Contract response for {player.full_name}: {result!r}\n"
            )
            self.status_var.set("Contract offer evaluated.")
        except Exception as exc:
            self._show_error("Contract offer", exc)

    def _process_transfers(self):
        try:
            controller = self._require_game()
            results = controller.process_due_transfers()
            self._write_transfer_output(
                "Due transfer processing:\n"
                + ("\n".join(repr(x) for x in results) if results else "No transfer due.")
                + "\n"
            )
            self._refresh_all()
        except Exception as exc:
            self._show_error("Transfers", exc)

    def _write_transfer_output(self, text: str):
        self.transfer_output.configure(state="normal")
        self.transfer_output.insert("end", text + "\n")
        self.transfer_output.see("end")
        self.transfer_output.configure(state="disabled")

    def _refresh_scout_results(self):
        if not hasattr(self, "scout_tree"):
            return
        self.scout_tree.delete(*self.scout_tree.get_children())
        if self.gameplay is None:
            return
        on_date = self.gameplay.state.calendar.current_date
        for player in self.scouting_results:
            status = []
            if player.transfer_listed:
                status.append("Transfer listed")
            if player.loan_listed:
                status.append("Loan listed")
            if player.out_of_contract:
                status.append("Out of contract")
            age = player.age(on_date)
            self.scout_tree.insert(
                "",
                "end",
                iid=str(player.index),
                values=(
                    player.index,
                    player.full_name,
                    self._club_name(int(player.club_id)),
                    "" if age is None else age,
                    self._position_name(int(player.positions[0])),
                    player.weekly_wage,
                    ", ".join(status),
                ),
            )

    # ---------- youth ----------

    def _build_youth(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Youth")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Button(
            controls,
            text="Initialize fresh youth",
            command=self._initialize_youth,
        ).pack(side="left")

        self.youth_wage = tk.IntVar(value=1_500)
        self.youth_months = tk.IntVar(value=24)
        ttk.Label(controls, text="Promotion wage").pack(side="left", padx=(14, 3))
        ttk.Entry(controls, textvariable=self.youth_wage, width=10).pack(side="left")
        ttk.Label(controls, text="Months").pack(side="left", padx=(8, 3))
        ttk.Entry(controls, textvariable=self.youth_months, width=6).pack(side="left")
        ttk.Button(
            controls, text="Promote", command=self._promote_youth
        ).pack(side="left", padx=(8, 4))
        ttk.Button(
            controls, text="Release", command=self._release_youth
        ).pack(side="left")

        self.youth_tree = ttk.Treeview(
            frame,
            columns=("id", "player", "age", "pos", "condition", "morale"),
            show="headings",
            selectmode="browse",
        )
        for col, title, width in (
            ("id", "ID", 55),
            ("player", "Player", 240),
            ("age", "Age", 45),
            ("pos", "Pos", 60),
            ("condition", "Cond", 60),
            ("morale", "Morale", 60),
        ):
            self.youth_tree.heading(col, text=title)
            self.youth_tree.column(col, width=width, anchor="w")
        self.youth_tree.pack(fill="both", expand=True)

    def _initialize_youth(self):
        try:
            controller = self._require_game()
            controller.initialize_fresh_youth()
            self.status_var.set("Fresh user youth list initialized.")
            self._refresh_youth()
        except Exception as exc:
            self._show_error("Youth", exc)

    def _selected_youth_id(self) -> int:
        sel = self.youth_tree.selection()
        if not sel:
            raise RuntimeError("Select a youth player.")
        return int(sel[0])

    def _promote_youth(self):
        try:
            controller = self._require_game()
            controller.promote_youth_player(
                self._selected_youth_id(),
                weekly_wage=float(self.youth_wage.get()),
                contract_months=int(self.youth_months.get()),
            )
            self.status_var.set("Youth player promoted.")
            self._refresh_all()
        except Exception as exc:
            self._show_error("Youth promotion", exc)

    def _release_youth(self):
        try:
            controller = self._require_game()
            controller.release_youth_player(self._selected_youth_id())
            self.status_var.set("Youth player released.")
            self._refresh_all()
        except Exception as exc:
            self._show_error("Youth release", exc)

    def _refresh_youth(self):
        if not hasattr(self, "youth_tree"):
            return
        self.youth_tree.delete(*self.youth_tree.get_children())
        if self.gameplay is None or self.gameplay.human is None:
            return
        on_date = self.gameplay.state.calendar.current_date
        try:
            players = self.gameplay.youth_players()
        except Exception:
            players = ()
        for player in players:
            age = player.age(on_date)
            self.youth_tree.insert(
                "",
                "end",
                iid=str(player.index),
                values=(
                    player.index,
                    player.full_name,
                    "" if age is None else age,
                    self._position_name(int(player.positions[0])),
                    player.condition,
                    player.morale,
                ),
            )

    # ---------- finances ----------

    def _build_finances(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Finances")

        self.cash_var = tk.StringVar(value="No controlled club")
        ttk.Label(
            frame, textvariable=self.cash_var, font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        objectives = ttk.LabelFrame(frame, text="Chairman financial objective", padding=8)
        objectives.pack(fill="x", pady=(10, 8))
        self.objective_var = tk.StringVar()
        self.objective_box = ttk.Combobox(
            objectives, textvariable=self.objective_var, state="readonly", width=44
        )
        self.objective_box.pack(side="left")
        ttk.Button(
            objectives, text="Select objective", command=self._select_objective
        ).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="Balance ledger").pack(anchor="w")
        self.ledger_tree = ttk.Treeview(
            frame,
            columns=("date", "category", "amount"),
            show="headings",
        )
        for col, title, width in (
            ("date", "Date", 110),
            ("category", "Category", 100),
            ("amount", "Amount", 140),
        ):
            self.ledger_tree.heading(col, text=title)
            self.ledger_tree.column(col, width=width, anchor="w")
        self.ledger_tree.pack(fill="both", expand=True)

    def _select_objective(self):
        try:
            controller = self._require_game()
            text = self.objective_var.get()
            if not text:
                raise RuntimeError("No objective candidate selected.")
            index = int(text.split(":", 1)[0])
            new_cash = controller.select_financial_objective(index)
            self.status_var.set(f"Financial objective selected. Cash: {new_cash}.")
            self._refresh_finances()
        except Exception as exc:
            self._show_error("Financial objective", exc)

    def _refresh_finances(self):
        if not hasattr(self, "ledger_tree"):
            return
        self.ledger_tree.delete(*self.ledger_tree.get_children())
        if self.gameplay is None or self.gameplay.human is None:
            self.cash_var.set("No controlled club")
            self.objective_box["values"] = ()
            self.objective_var.set("")
            return

        club_id = int(self.gameplay.human.club_id)
        balance = self.gameplay.state.finance_balances.get(club_id)
        if balance is None:
            self.cash_var.set("No materialized Balance state")
            return
        self.cash_var.set(
            f"{self._club_name(club_id)} current cash: {balance.current_cash:,.2f}"
        )

        try:
            candidates = self.gameplay.financial_objective_candidates()
            values = tuple(
                f"{index}: objective {objective_id}"
                for index, objective_id in enumerate(candidates)
            )
            self.objective_box["values"] = values
            if values and self.objective_var.get() not in values:
                self.objective_var.set(values[0])
        except Exception:
            pass

        for posting in reversed(balance.ledger):
            self.ledger_tree.insert(
                "",
                "end",
                values=(
                    posting.posting_date.isoformat(),
                    posting.category,
                    f"{float(posting.amount):,.2f}",
                ),
            )

    # ---------- inbox ----------

    def _build_inbox(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Inbox")

        ttk.Label(
            frame,
            text="Recovered manager events",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                "This is a temporary event viewer for reconstructed contract-renewal "
                "and player transfer-request queues. Original message presentation "
                "belongs to the later UI gate."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 8))

        self.inbox_text = tk.Text(
            frame, wrap="word", font=("Consolas", 10), state="disabled"
        )
        self.inbox_text.pack(fill="both", expand=True)

    def _refresh_inbox(self):
        if not hasattr(self, "inbox_text"):
            return
        lines = []
        if self.gameplay is None:
            lines.append("Start a game to materialize runtime events.")
        else:
            state = self.gameplay.state
            lines.append("Contract renewal suggestions:")
            if state.contract_renewal_suggestions:
                lines.extend(f"  {item!r}" for item in state.contract_renewal_suggestions)
            else:
                lines.append("  None")
            lines.append("")
            lines.append("Player transfer requests:")
            if state.player_transfer_requests:
                lines.extend(f"  {item!r}" for item in state.player_transfer_requests)
            else:
                lines.append("  None")
            lines.append("")
            lines.append(f"Manager sacking reason: {state.user_sacking_reason!r}")

        self.inbox_text.configure(state="normal")
        self.inbox_text.delete("1.0", "end")
        self.inbox_text.insert("1.0", "\n".join(lines))
        self.inbox_text.configure(state="disabled")

    # ---------- status ----------

    def _build_status(self):
        frame = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(frame, text="Build Status")
        text = (
            "CURRENT PLAYABLE SNAPSHOT\n\n"
            "Backed by the reconstructed runtime at the Gate-12 branch point.\n\n"
            "Exposed in this shell:\n"
            "  • canonical FM2001 database loading\n"
            "  • Premier League + current domestic Cup matchday path\n"
            "  • human team selection, formations and tactics\n"
            "  • league table and match results\n"
            "  • save/load using the modern internal save format\n"
            "  • training method assignment\n"
            "  • scouting search and ordinary cash transfer workflow\n"
            "  • live Balance/current cash and chairman objective selection\n"
            "  • youth initialization, promotion and release\n"
            "  • recovered contract-renewal / transfer-request event queues\n\n"
            "Deliberately NOT claimed here:\n"
            "  • original FM2001 presentation/UI fidelity\n"
            "  • original save-file compatibility\n"
            "  • full competition world beyond currently integrated Gate-12 coverage\n"
            "  • original FastView/3D/audio presentation\n"
            "  • fidelity work that remains open in CURRENT_STATE.md\n\n"
            "The active implementation worker remains authoritative for backend "
            "reconstruction. This branch is a separately isolated play-test surface."
        )
        ttk.Label(
            frame, text=text, justify="left", font=("Segoe UI", 11)
        ).pack(anchor="nw")

    # ---------- save/load ----------

    def _save_game(self):
        try:
            controller = self._require_game()
            path = filedialog.asksaveasfilename(
                title="Save FM2001 modern game",
                defaultextension=".fm2k",
                filetypes=(("FM2001 modern save", "*.fm2k"), ("All files", "*.*")),
                initialfile="fm2001-current-snapshot.fm2k",
            )
            if not path:
                return
            save_human_gameplay(controller, path)
            self.status_var.set(f"Saved {Path(path).name}.")
        except Exception as exc:
            self._show_error("Save game", exc)

    def _load_game(self):
        try:
            path = filedialog.askopenfilename(
                title="Load FM2001 modern game",
                filetypes=(("FM2001 modern save", "*.fm2k"), ("All files", "*.*")),
            )
            if not path:
                return
            runtime = self._ensure_gameplay()
            self.gameplay = load_human_gameplay(
                self.db,
                runtime.attack_matrix,
                runtime.defence_matrix,
                path,
            )
            self._sync_loaded_ui()
            self.status_var.set(f"Loaded {Path(path).name}.")
            self._refresh_all()
        except Exception as exc:
            self._show_error("Load game", exc)

    def _sync_loaded_ui(self):
        self.selected_starters.clear()
        self.selected_subs.clear()
        if self.gameplay is None or self.gameplay.human is None:
            return
        human = self.gameplay.human
        self.club_var.set(f"{human.club_id}: {self._club_name(human.club_id)}")
        self.formation_var.set(int(human.formation_id))
        self.selected_starters.update(int(x) for x in human.starter_ids)
        self.selected_subs.update(int(x) for x in human.substitute_ids)
        tactics = self.gameplay.state.team_tactics.get(int(human.club_id))
        if tactics is not None:
            self.play_style_var.set(int(tactics.play_style))
            self.without_ball_var.set(int(tactics.without_ball_style))
            self.with_ball_var.set(int(tactics.with_ball_style))
            self.aggression_var.set(int(tactics.aggression))
        if self.gameplay.pending_primary_entry is not None:
            self.match_var.set(
                self._entry_description(tuple(self.gameplay.pending_primary_entry))
            )

    # ---------- refresh ----------

    def _refresh_home(self):
        lines = [
            f"Database: {self.db.summary()}",
            f"Game files: {self.game_dir}",
            "",
        ]
        if self.gameplay is None or self.gameplay.human is None:
            lines.append("No human manager game has been started.")
        else:
            controller = self.gameplay
            human = controller.human
            lines.extend(
                (
                    f"Club: {self._club_name(human.club_id)}",
                    f"Date: {controller.state.calendar.current_date.isoformat()}",
                    f"Squad size: {len(controller.squad())}",
                    f"Pending match: {self._entry_description(controller.pending_primary_entry)}",
                    f"Scheduled transfers: {len(controller.state.transfers.scheduled_transfers)}",
                    f"Contract renewal messages: {len(controller.state.contract_renewal_suggestions)}",
                    f"Player transfer requests: {len(controller.state.player_transfer_requests)}",
                )
            )
            balance = controller.state.finance_balances.get(int(human.club_id))
            if balance is not None:
                lines.append(f"Current cash: {float(balance.current_cash):,.2f}")

        self.home_summary.configure(state="normal")
        self.home_summary.delete("1.0", "end")
        self.home_summary.insert("1.0", "\n".join(lines))
        self.home_summary.configure(state="disabled")

    def _refresh_all(self):
        if self.gameplay is not None:
            self.date_var.set(self.gameplay.state.calendar.current_date.isoformat())
        else:
            self.date_var.set("No game started")
        self._refresh_home()
        self._refresh_squad()
        self._refresh_lineup()
        self._refresh_table()
        self._refresh_scout_results()
        self._refresh_youth()
        self._refresh_finances()
        self._refresh_inbox()


def choose_dir() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title="Select FM2001 game folder")
    root.destroy()
    return Path(selected) if selected else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game_dir", nargs="?", default=str(DEFAULT_GAME_DIR))
    args = parser.parse_args()

    game_dir = Path(args.game_dir)
    required = ("Master.dat", "Static.dat", "Core.str", "English.str", "FOOTBAL.EXE")
    if not all((game_dir / name).exists() for name in required):
        game_dir = choose_dir()
        if game_dir is None:
            return

    try:
        CurrentPlayableSnapshot(game_dir).mainloop()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("FM2001 playable snapshot", str(exc))
        root.destroy()
        raise


if __name__ == "__main__":
    main()
