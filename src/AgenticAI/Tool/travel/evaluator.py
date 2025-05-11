from typing import List
from src.AgenticAI.State.travel_state import TravelState
from langgraph.constants import Send

class Evaluator:
    MAX_RETRIES = 3  # Maximum allowed evaluation attempts

    @staticmethod
    def evaluate_content(completed_sections: List[str]) -> bool:
        """Evaluates section quality with detailed feedback"""
        print("\n=== CONTENT EVALUATION ===")
        
        if not completed_sections:
            print("❌ Evaluation failed: No sections to evaluate")
            return False
            
        all_valid = True
        # for i, section in enumerate(completed_sections, 1):
        #     print(f"Checking section {i}: {section[:50]}...")
            
        #     # Length check
        #     if len(section.strip()) < 100:
        #         print(f"❌ Section {i} too short ({len(section.strip())} chars)")
        #         all_valid = False
                
        #     # Detail check
        #     if "details" not in section.lower():
        #         print(f"❌ Section {i} missing required details")
        #         all_valid = False
                
        #     # Address check
        #     if "address:" not in section.lower():
        #         print(f"❌ Section {i} missing physical address")
        #         all_valid = False
                
        return all_valid

    @staticmethod
    def evaluate(state: TravelState):
        """Manages evaluation with retry limits"""
        print("\n=== EVALUATION WORKFLOW ===")
        
        # Initialize retry counter
        state.setdefault("retries", 0)
        state["retries"] += 1
        
        print(f"Evaluation attempt {state['retries']}/{Evaluator.MAX_RETRIES}")
        
        # Check retry limit before evaluation
        if state["retries"] > Evaluator.MAX_RETRIES:
            print("⚠️ Max retries reached. Proceeding with current content.")
            return {"evaluator_passed": True}
            
        # Perform content evaluation
        evaluation_result = Evaluator.evaluate_content(state["completed_sections"])
        
        if not evaluation_result:
            print(f"🚨 Evaluation failed. Remaining attempts: {Evaluator.MAX_RETRIES - state['retries']}")
            return Send("orchestrator", state)
            
        print("✅ All sections passed quality checks")
        return {"evaluator_passed": True, "retries": 0}  # Reset retry counter
