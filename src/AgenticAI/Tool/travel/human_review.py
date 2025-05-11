from typing import List
from src.AgenticAI.State.travel_state import TravelState
from langgraph.constants import Send

class HumanReview:
    @staticmethod
    def collect_feedback(sections: List[str]) -> str:
        """Simulates human feedback collection"""
        print("\n=== HUMAN REVIEW PHASE ===")
        print("Reviewing travel plan sections:")
        
        for i, section in enumerate(sections, 1):
            print(f"Section {i}: {section[:100]}...")
            
        # In a production system, this would collect actual human input
        feedback = "Ensure all attractions include exact details like hours, addresses, and tips."
        print(f"Human feedback received: '{feedback}'")
        return feedback

    @staticmethod
    def apply_feedback(sections: List[str], feedback: str) -> List[str]:
        """Applies human feedback to the sections"""
        print("Applying human feedback to sections.")
        updated_sections = []
        for section in sections:
            updated_sections.append(f"{section}\n\nHuman Feedback: {feedback}")
        return updated_sections

    def review(self, state: TravelState):
        """Manages the human-in-the-loop feedback process"""
        if not state.get("completed_sections"):
            return Send("orchestrator", state)
            
        feedback = self.collect_feedback(state["completed_sections"])
        
        if not feedback:
            return {"status": "no_feedback", "next_step": "synthesizer"}
            
        updated_sections = self.apply_feedback(state["completed_sections"], feedback)
        
        # For substantial changes, route back to orchestrator
        if "major" in feedback.lower() or "rewrite" in feedback.lower():
            updated_state = dict(state)
            updated_state["completed_sections"] = updated_sections
            return Send("orchestrator", updated_state)
            
        return {
            "completed_sections": updated_sections,
            "status": "feedback_applied", 
            "next_step": "synthesizer"
        }
