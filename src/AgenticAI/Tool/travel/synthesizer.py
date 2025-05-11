from src.AgenticAI.State.travel_state import TravelState

class Synthesizer:
    def synthesize(self, state: TravelState):
        """Combines all sections into a final travel report"""
        print("\n=== SYNTHESIS PHASE ===")
        
        if not state.get("completed_sections"):
            return {"final_report": "No content available for the travel plan."}
            
        # Combine all sections with section separators
        final_report = "\n\n---\n\n".join(state["completed_sections"])
        
        # Add a title based on the topic
        if state.get("topic"):
            final_report = f"# Travel Plan: {state['topic']}\n\n{final_report}"
            
        print(f"Final report synthesized ({len(final_report)} characters).")
        return {"final_report": final_report}
