"""Source-closed nested FastView score/team draw-array algorithms.

This module intentionally models counts and mutation order instead of claiming one
immutable global z-order. The outer FastViewScores/FastViewTeam wrappers are already
source-ordered. Their nested child arrays are source-parameterized and, for score
phase indicators, dynamically mutated at runtime.
"""
from __future__ import annotations
from dataclasses import dataclass

class FastViewNestedOrderError(ValueError):
    pass

LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA=0x51E000
LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA=0x51DCB0
LEAGUE_TABLE_ROW_CONSTRUCTOR_VA=0x51D730
LEAGUE_HEADING_CONTROL_COUNT=8
LEAGUE_ROW_CONTROL_COUNT=10
LEAGUE_ROW_SPLIT_THRESHOLD=12

TEAM_TABLE_CONSTRUCTOR_VA=0x524EC0
TEAM_PLAYERROW_CONSTRUCTOR_VA=0x525DB0
TEAM_TABLE_BASE_CONTROL_COUNT=6
TEAM_PLAYERROW_CONTROL_COUNT=9
TEAM_FIXED_PLAYERROW_COUNT=11
TEAM_SIDE0_FACTORY_CALL_VA=0x524C4F
TEAM_SIDE1_FACTORY_CALL_VA=0x524DBB

SCORE_COMPOSITE_FACTORY_VA=0x523CC0
SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA=0x51B740
SCORE_COMPOSITE_BASE_CONSTRUCTOR_VA=0x51A730
SCORE_COMPOSITE_STATIC_CONTROL_COUNT=5
SCORE_PHASE_SET_VA=0x51BA30
SCORE_PHASE_CLEAR_VA=0x51BBE0
SCORE_PHASE_DYNAMIC_CONTROL_COUNT=2

def league_table_display_row_count(source_count:int)->int:
    if type(source_count) is not int or source_count<=0:
        raise FastViewNestedOrderError("source_count must be positive")
    if source_count<=LEAGUE_ROW_SPLIT_THRESHOLD:
        return source_count
    return (source_count+1)//2

def league_table_visible_control_count(source_count:int)->int:
    return LEAGUE_HEADING_CONTROL_COUNT + LEAGUE_ROW_CONTROL_COUNT*league_table_display_row_count(source_count)

def team_table_playerrow_count(source_player_count:int)->int:
    if type(source_player_count) is not int or source_player_count<0:
        raise FastViewNestedOrderError("source_player_count must be non-negative")
    return max(TEAM_FIXED_PLAYERROW_COUNT,source_player_count)

def team_table_visible_control_count(source_player_count:int)->int:
    return TEAM_TABLE_BASE_CONTROL_COUNT + TEAM_PLAYERROW_CONTROL_COUNT*team_table_playerrow_count(source_player_count)

@dataclass(frozen=True)
class ScoreCompositePhaseTail:
    static_controls:int=SCORE_COMPOSITE_STATIC_CONTROL_COUNT
    phase_controls:int=0
    mutation_generation:int=0
    def __post_init__(self):
        if self.static_controls!=5 or self.phase_controls not in (0,2) or self.mutation_generation<0:
            raise FastViewNestedOrderError("invalid score phase-tail state")
    @property
    def visible_controls(self)->int:
        return self.static_controls+self.phase_controls
    def clear(self)->"ScoreCompositePhaseTail":
        return ScoreCompositePhaseTail(5,0,self.mutation_generation+1)
    def set_phase(self)->"ScoreCompositePhaseTail":
        # 0x51BA30 calls 0x51BBE0 first, then appends PictureControl followed by TextControl.
        return ScoreCompositePhaseTail(5,2,self.mutation_generation+1)

def nested_order_contract()->dict:
    return {
      "league_table_heading_controls":8,
      "league_table_row_controls":10,
      "league_table_rows_source_parameterized":True,
      "team_table_base_controls":6,
      "team_playerrow_controls":9,
      "team_playerrows_source_parameterized":True,
      "score_composite_static_controls":5,
      "score_phase_tail_controls":2,
      "score_phase_tail_runtime_mutation_recovered":True,
      "single_immutable_nested_order":False,
      "global_fastview_z_order_recovered":False,
      "complete_fastview_frame_recovered":False,
    }
