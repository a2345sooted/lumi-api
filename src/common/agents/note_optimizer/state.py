from typing import List, Optional
from typing_extensions import TypedDict

class NoteDict(TypedDict):
    content: str
    note_type: str

class NoteOptimizerState(TypedDict):
    user_id: str
    thread_id: Optional[str]
    original_notes: List[NoteDict]
    optimized_notes: List[NoteDict]
