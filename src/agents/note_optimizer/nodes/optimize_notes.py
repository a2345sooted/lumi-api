from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.note_optimizer.state import NoteOptimizerState, NoteDict
from src.ai_constants import OPENAI_MODEL_4O_MINI

from src.database import SessionLocal
from src.repos.notes import UserNoteRepository

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
            "Your goal is to take a list of user notes and optimize them. "
            "1. Remove duplicate information. "
            "2. Consolidate related notes into clearer, more concise notes without losing any information. "
            "3. Maintain the note_type (Profile or Dynamic). Profile notes should contain personal identity information (name, email, etc.). "
            "4. If multiple Profile notes exist, consolidate them into a single Profile note if possible. "
            "5. Resolve contradictions: If two notes contradict each other, use the 'Created' timestamp to determine which one is more recent. The more recent note should take precedence. "
            "6. Return the final list of optimized notes."
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
