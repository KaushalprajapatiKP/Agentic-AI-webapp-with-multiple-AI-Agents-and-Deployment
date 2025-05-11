from langgraph.constants import Send
from typing import TypedDict, List, Dict
from typing_extensions import Annotated
import operator
from pydantic import BaseModel, Field



class ItinerarySection(BaseModel):
    name: str = Field(description="Category like Flights, Hotels, Attractions, or Notes.")
    description: str = Field(description="Details, bookings, recommendations, etc.")

class TravelItinerary(BaseModel):
    sections: List[ItinerarySection] = Field(description="Organized travel sections.")


# class TravelState(TypedDict):
#     topic: str # Topic of the report 
#     sections: List[ItinerarySection] # List of itinerary sections
#     completed_sections: Annotated[List[str], operator.add] # Sections completed by workers
#     final_report: str # Final synthesized travel plan
#     evaluator_passed: bool # To track if evaluation passed or not
class TravelState(TypedDict):
    topic: str
    sections: Annotated[List[ItinerarySection], operator.add]  # Modified line
    completed_sections: Annotated[List[str], operator.add]
    final_report: str
    evaluator_passed: bool
    retries: int
    response: str


# worker state for generating individual report sections
class WorkerState(TypedDict):
    section: ItinerarySection # A specific section of the travel itinerary
    completed_sections: Annotated[List[str], operator.add]

