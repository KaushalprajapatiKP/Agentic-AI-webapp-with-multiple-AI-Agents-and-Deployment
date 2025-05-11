from langchain_core.messages import SystemMessage, HumanMessage
from src.AgenticAI.State.travel_state import TravelState, TravelItinerary

class TravelPlanGenerator:
    def __init__(self, planner, state):
        self.planner = planner
        self.state = state

    def generate_travel_plan(self):
        """Generate a structured travel plan with sections"""
        try:
            travel_plan = self.planner.invoke([
                SystemMessage(content="Generate a comprehensive travel plan with detailed sections."),
                HumanMessage(content=f"Create a detailed travel itinerary for: {self.state['topic']}")
            ])
            return {"sections": travel_plan.sections}
        except Exception as e:
            print(f"Error generating travel plan: {str(e)}")
            return {"sections": []}

class TravelOrchestrator:
    def __init__(self, planner, state=None):
        self.planner = planner
        self.state = state or {}
        self.travel_plan_generator = TravelPlanGenerator(planner, self.state)

    def orchestrate(self, state: TravelState, planner=None):
        """Orchestrate the travel plan generation process"""
        # Update state if provided
        if state:
            self.travel_plan_generator.state = state
        
        # Use provided planner or default
        if planner:
            self.travel_plan_generator.planner = planner
        
        # Check if topic contains travel-related terms
        topic = self.travel_plan_generator.state.get('topic', '').lower()
        travel_keywords = {'travel', 'itinerary', 'trip', 'vacation', 'holiday', 'tour', 'journey'}
        
        if not any(keyword in topic for keyword in travel_keywords):
            print("I am a travel planner. I don't know anything else.")
            return {"response": "I am a travel planner. I don't know anything else."}
        else:
            result = self.travel_plan_generator.generate_travel_plan()
            print(f"Travel Plan generated with {len(result['sections'])} sections:")
            for i, section in enumerate(result["sections"], 1):
                print(f"{i}. {section.name}: {section.description[:50]}...")
            return {"sections": result["sections"]}