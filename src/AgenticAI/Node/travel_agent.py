from typing import List
from pydantic import BaseModel, Field



# Define the sections of the travel plan
class ItinerarySection(BaseModel):
    name: str = Field(
        description="Category of the itinerary section, such as Flights, Hotels, Attractions, or Notes."
    )
    description: str = Field(
        description="Details about this part of the travel itinerary, including recommendations, bookings, or human suggestions."
    )

# Full travel plan composed of multiple sections
class TravelItinerary(BaseModel):
    sections: List[ItinerarySection] = Field(
        description="Detailed travel plan organized into sections like flights, hotels, attractions, and human feedback."
    )


planner = llm.with_structured_output(TravelItinerary)

from langgraph.constants import Send
from typing import TypedDict, List, Dict
from typing_extensions import Annotated
import operator


class State(TypedDict):
    topic: str # Topic of the report 
    sections: List[ItinerarySection] # List of itinerary sections
    completed_sections: Annotated[List[str], operator.add] # Sections completed by workers
    final_report: str # Final synthesized travel plan
    evaluator_passed: bool # To track if evaluation passed or not

# worker state for generating individual report sections
class WorkerState(TypedDict):
    section: ItinerarySection # A specific section of the travel itinerary
    completed_sections: Annotated[List[str], operator.add]

# Orchestrator: Generates a plan for the travel report
from langchain_core.messages import SystemMessage, HumanMessage
def orchestrator(state: State):
    """ Orchestrator is responsible for generating a plan for travel via dynamically generated workers"""
    travel_plan = planner.invoke(
        [
            SystemMessage(content="Generate a travel plan based on the sections."),
            HumanMessage(content=f"here is the itinerary: {state['topic']}",)
        ]
    )

    print("Travel Plan Sections:", travel_plan)
    # Return the sections of the travel plan
    return {"sections": travel_plan.sections}


# Worker: Writes the content for a section of the itinerary
def llm_call(state: WorkerState):
    """Worker generates content for a specific section of the travel itinerary"""

    # Generate the content for the section using the LLM
    section_content = llm.invoke(
        [
            SystemMessage(
                content="Write a section for the travel plan. Include no preamble for each section. Use markdown formatting."
            ),
            HumanMessage(
                content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
            ),
        ]
    )

    # Append the generated section to the completed sections list
    return {"completed_sections": [section_content.content]}


# Evaluator: Evaluate the generated travel plan content
def evaluator(state: State):
    """Evaluates the generated travel plan sections for quality"""

    # Example evaluation logic: Check if each section contains the required level of detail
    evaluation_result = evaluate_content(state["completed_sections"])

    if not evaluation_result:
        # If evaluation fails, return to orchestrator for more work
        print("Evaluation failed, sending back to orchestrator.")
        return Send("orchestrator", state)

    # If evaluation passes, set the evaluator flag and continue
    print("Evaluation passed, proceeding to In-Human.")
    return {"evaluator_passed": True}

def evaluate_content(completed_sections: List[str]) -> bool:
    """Custom function to evaluate the quality of the sections"""

    # Example: Check if sections contain enough content or if certain required details are missing
    for section in completed_sections:
        if len(section.strip()) < 100:  # Example: Section must be at least 50 characters long
            print(f"Evaluation failed: Section too short.")
            return False
        if "details" not in section.lower():  # Example: Section must include the word 'details'
            print(f"Evaluation failed: Missing 'details' in section.")
            return False
    return True

def in_human(state: State):
    """Allow for human adjustments or final review before completing the travel plan"""

    # Collect human feedback or allow for manual adjustments
    human_feedback = collect_human_feedback(state["completed_sections"])

    if not human_feedback:  # If no feedback is provided, return to orchestrator
        print("No feedback received. Returning to orchestrator for further processing.")
        return {"status": "no_feedback", "next_step": "orchestrator"}

    # Apply human feedback to the sections
    updated_sections = apply_human_feedback(state["completed_sections"], human_feedback)

    # Finalize the travel plan with the updated sections
    return {"final_report": "\n\n---\n\n".join(updated_sections), "status": "feedback_applied", "next_step": "synthesizer"}

def collect_human_feedback(completed_sections: List[str]) -> str:
    """Function to collect feedback from a human (e.g., via UI or manual input)"""
    
    # Example logic to collect feedback from a human user
    print("Collecting feedback for the following sections:")

    for i, section in enumerate(completed_sections, 1):
        print(f"{i}. {section[:100]}...")  # Display first 100 chars of each section for review

    # Simulate asking the human for feedback (e.g., via a UI or command-line input)
    feedback = "Ensure that all travel attractions are listed with exact details on opening hours, addresses, and special tips."

    print("Feedback collected:", feedback)
    return feedback

def apply_human_feedback(completed_sections: List[str], feedback: str) -> List[str]:
    """Apply human feedback to the completed sections"""
    
    # Example logic: Append the feedback to the last section or modify sections as required
    print(f"Applying feedback: {feedback}")
    completed_sections[-1] += f"\n\nHuman Feedback: {feedback}"
    return completed_sections
# Synthesizer: Combines all completed sections into a full travel plan
def synthesizer(state: State):
    """Combine all completed sections into a full travel plan"""

    # Gather all completed sections
    completed_sections = state["completed_sections"]

    # Join the sections together with markdown formatting
    completed_travel_plan = "\n\n---\n\n".join(completed_sections)

    # Return the final synthesized travel plan
    return {"final_report": completed_travel_plan}

# Conditional edge function to create llm_call workers that each write a section of the travel itinerary
def assign_workers(state: State):
    """Assign a worker to each section in the travel plan"""

    # Send tasks to workers to generate content for each section in parallel
    return [Send("llm_call", {"section": s}) for s in state["sections"]]


# Graph Bulding
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

orchestrator_graph_builder = StateGraph(State)

orchestrator_graph_builder.add_node(
    "orchestrator",
    orchestrator,
)
orchestrator_graph_builder.add_node(
    "llm_call",
    llm_call,
)
orchestrator_graph_builder.add_node(
    "synthesizer",
    synthesizer,
)
orchestrator_graph_builder.add_node(
    "evaluator",
    evaluator,
)
orchestrator_graph_builder.add_node(
    "in_human",
    in_human,
)



orchestrator_graph_builder.add_edge(
    START,
    "orchestrator",
)
orchestrator_graph_builder.add_conditional_edges(
    "orchestrator", 
    assign_workers, 
    ["llm_call"]
)
orchestrator_graph_builder.add_edge(
    "llm_call",
    "evaluator",
)
orchestrator_graph_builder.add_conditional_edges(
    "evaluator",
    evaluate_content,
    "orchestrator",
    # condition=lambda state: state.get('evaluation_status') == False
)
orchestrator_graph_builder.add_edge(
    "evaluator",
    "in_human",
    # condition=lambda state: state.get('evaluation_status') == True
)
orchestrator_graph_builder.add_conditional_edges(
    "in_human",
    in_human,  
    "orchestrator", 
    # condition=lambda state: state.get('status') == 'no_feedback'
)
orchestrator_graph_builder.add_edge(
    "in_human",
    "synthesizer",
    # condition=lambda state: state.get('status') == 'feedback_applied'
)
orchestrator_graph_builder.add_edge(
    "synthesizer",
    END,
)

# compile the workflow
travel_agent = orchestrator_graph_builder.compile()

# Run the workflow
state = travel_agent.invoke(
    {
        "topic": "Travel Itinerary for a trip to Paris",
    }
)

# Display the final report
print("Final Report:", state["final_report"])
# Display the grap