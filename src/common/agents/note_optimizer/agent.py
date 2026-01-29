from langgraph.graph import StateGraph, START, END
from src.common.agents.note_optimizer.state import NoteOptimizerState
from src.common.agents.note_optimizer.nodes.load_notes import load_notes_node
from src.common.agents.note_optimizer.nodes.optimize_notes import optimize_notes_node
from src.common.agents.note_optimizer.nodes.update_notes import update_notes_node

def compile_note_optimizer_agent():
    workflow = StateGraph(NoteOptimizerState)
    
    workflow.add_node("load_notes", load_notes_node)
    workflow.add_node("optimize_notes", optimize_notes_node)
    workflow.add_node("update_notes", update_notes_node)
    
    workflow.add_edge(START, "load_notes")
    workflow.add_edge("load_notes", "optimize_notes")
    workflow.add_edge("optimize_notes", "update_notes")
    workflow.add_edge("update_notes", END)
    
    return workflow.compile()
