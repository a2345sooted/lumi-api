from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.common.agents.note_optimizer.state import NoteOptimizerState, NoteDict
from src.common.ai_constants import OPENAI_MODEL_4O_MINI

from src.common.database import SessionLocal
from src.common.repos.notes import UserNoteRepository

class OptimizedNotes(BaseModel):
    notes: List[NoteDict] = Field(description="The list of optimized and consolidated notes.")

async def optimize_notes_node(state: NoteOptimizerState):
    db = SessionLocal()
    try:
        llm = ChatOpenAI(model=OPENAI_MODEL_4O_MINI, temperature=0)
        structured_llm = llm.with_structured_output(OptimizedNotes)
        
        notes_to_optimize = state.get("original_notes", [])
        
        if not notes_to_optimize:
            return {"optimized_notes": []}
        
        notes_str = "\n".join([f"[{n['note_type']}] (Created: {n['created_at']}) {n['content']}" for n in notes_to_optimize])
        
        system_prompt = (
            "You are an expert at information consolidation and deduplication. "
            "Your goal is to take a list of user notes and optimize them into a clean, structured knowledge base. "
            "\n\nRules:\n"
            "1. Remove duplicate information.\n"
            "2. Profile Information: Identify notes that contain personal identity information (e.g., name, email, location, profession, birthdate). "
            "Consolidate ALL profile information into a single note with note_type 'Profile'. "
            "The content of this note MUST be a single JSON object containing all identified profile fields.\n"
            "3. Related Dynamic Notes: Identify groups of dynamic notes that are closely related (e.g., all notes about 'hobbies', 'family', 'travel preferences', or 'work projects'). "
            "Consolidate each related group into a single note with note_type 'Dynamic'. "
            "The content of these consolidated notes SHOULD be a JSON object if they contain multiple distinct but related pieces of information. "
            "Unrelated dynamic notes should remain as separate string-based or simple JSON notes.\n"
            "4. Contradictions: If two notes contradict each other, use the '(Created: timestamp)' prefix to determine which one is more recent. The more recent information MUST take precedence.\n"
            "5. Preservation: Ensure no unique or important information is lost during consolidation.\n"
            "6. Output: Return a list of optimized notes, where each note has 'content' (string, which can be a JSON string) and 'note_type' ('Profile' or 'Dynamic')."
        )
        
        human_prompt = f"Here are the notes to optimize:\n\n{notes_str}"
        
        response = await structured_llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        
        return {
            "optimized_notes": response.notes
        }
    except Exception as e:
        repo = UserNoteRepository(db)
        repo.end_optimization_run(state.get("user_id"), status="FAILED")
        raise e
    finally:
        db.close()
