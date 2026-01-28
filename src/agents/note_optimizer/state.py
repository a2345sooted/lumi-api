from typing import TypedDict, List

class NoteDict(TypedDict):
    content: str
    note_type: str

class NoteOptimizerState(TypedDict):
    user_id: str
    original_notes: List[NoteDict]
    optimized_notes: List[NoteDict]
