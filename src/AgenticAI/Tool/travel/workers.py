from src.AgenticAI.State.travel_state import WorkerState
from langchain_core.messages import SystemMessage, HumanMessage

class Worker:
    def __init__(self, llm):
        self.llm = llm

    def generate_section(self, state: WorkerState):
        """Worker generates detailed content for a specific section"""
        section = state.get("section")
        if not section:
            print("Error: No section provided to worker.")
            return {"completed_sections": ["Error: No section details provided."]}
            
        print(f"\n=== GENERATING CONTENT FOR SECTION: {section.name} ===")
        
        try:
            system_prompt = """
            Write a detailed section for a travel plan. Include:
            - Exact addresses and locations
            - Opening hours and availability
            - Booking information and reservation details
            - Cost estimates and budget considerations
            - Local tips and recommendations
            - Transportation options
            
            Use markdown formatting. Focus on specific details that travelers need.
            """
            
            section_content = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(
                        content=f"Write the '{section.name}' section with this description: {section.description}"
                    ),
                ]
            )
            
            content = section_content.content
            print(f"Generated {len(content)} characters for '{section.name}'")
            
            return {"completed_sections": [content]}
            
        except Exception as e:
            print(f"Error generating section content: {str(e)}")
            return {"completed_sections": [f"Error generating content for {section.name}: {str(e)}"]}
