from typing import TypedDict, List, Optional

class NoteDict(TypedDict):
    content: str
    note_type: str

class NoteOptimizerState(TypedDict):
    user_id: str
    thread_id: Optional[str]
    original_notes: List[NoteDict]
    optimized_notes: List[NoteDict]
