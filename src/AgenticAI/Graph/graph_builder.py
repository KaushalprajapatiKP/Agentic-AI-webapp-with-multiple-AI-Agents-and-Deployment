from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import  tools_condition, ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.constants import Send

from src.AgenticAI.State.state import State
from src.AgenticAI.Node.basic_chatbot_node import BasicChatbotNode
from src.AgenticAI.Node.chatbot_with_Tool_node import ChatBotWithToolNode
from src.AgenticAI.Tool.search_tool import get_tools, create_tool_node

from typing import List


# === Chatbot-specific imports ===
from src.AgenticAI.State.state import State as ChatState
from src.AgenticAI.Node.basic_chatbot_node import BasicChatbotNode
from src.AgenticAI.Node.chatbot_with_Tool_node import ChatBotWithToolNode
from src.AgenticAI.Tool.search_tool import get_tools, create_tool_node


# === Travel Itinerary-specific imports ===
from src.AgenticAI.State.travel_state import TravelItinerary, TravelState, WorkerState
from src.AgenticAI.Tool.travel.evaluator import Evaluator
from src.AgenticAI.Tool.travel.human_review import HumanReview
from src.AgenticAI.Tool.travel.synthesizer import Synthesizer
from src.AgenticAI.Tool.travel.workers import Worker
from src.AgenticAI.Tool.travel.orchestrator import TravelOrchestrator


class GraphBuilder:
    def __init__(self, model):
        self.llm = model    
        self.graph_builder = StateGraph(State)
    
    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.basic_chatbot_node = BasicChatbotNode(self.llm)
        self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
        

    def chatbot_with_tools_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node 
        and a tool node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """
        ## Define the tool and tool node

        tools=get_tools()
        tool_node=create_tool_node(tools)

        ##Define LLM
        llm = self.llm

        # Define chatbot node
        obj_chatbot_with_node = ChatBotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)

        # Add nodes
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)

        # Define conditional and direct edges
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools","chatbot")

    # === TRAVEL ITINERARY ===
    def build_travel_itinerary_graph(self):
        """Builds the complete travel itinerary workflow graph"""
        print("\n==== BUILDING TRAVEL ITINERARY GRAPH ====")
        self.graph_builder = StateGraph(TravelState)

        # Initialize components
        worker = Worker(self.llm)
        evaluator = Evaluator()
        human = HumanReview()
        synth = Synthesizer()
        planner = self.llm.with_structured_output(TravelItinerary)
        orchestrator = TravelOrchestrator(planner=planner, state={})

        # Add nodes
        self.graph_builder.add_node("orchestrator", orchestrator.orchestrate)
        self.graph_builder.add_node("llm_call", worker.generate_section)
        self.graph_builder.add_node("evaluator", evaluator.evaluate)
        self.graph_builder.add_node("in_human", human.review)
        self.graph_builder.add_node("synthesizer", synth.synthesize)

        # Worker assignment function using the Send API
        def assign_workers(state: TravelState):
            """Creates worker tasks for each section using Send"""
            return [Send("llm_call", {"section": s}) for s in state["sections"]]

        # Set up the graph edges
        self.graph_builder.add_edge(START, "orchestrator")
        self.graph_builder.add_conditional_edges(
            "orchestrator", 
            assign_workers, 
            ["llm_call"]
        )
        self.graph_builder.add_edge("llm_call", "evaluator")

        # Conditional routing based on evaluation
        def evaluation_router(state: TravelState):
            return "in_human" if state.get("evaluator_passed", False) else "orchestrator"
                
        self.graph_builder.add_conditional_edges(
            "evaluator", 
            evaluation_router,
            {"orchestrator": "orchestrator", "in_human": "in_human"}
        )
        
        # Human review conditional routing
        def human_review_router(state: TravelState):
            return "orchestrator" if state.get("next_step") == "orchestrator" else "synthesizer"
                
        self.graph_builder.add_conditional_edges(
            "in_human",
            human_review_router,
            {"orchestrator": "orchestrator", "synthesizer": "synthesizer"}
        )

        # Final edge
        self.graph_builder.add_edge("synthesizer", END)
        print("Travel itinerary graph built successfully.")


    def setup_graph(self, usecase: str):
        """
        Sets up the graph based on the selected use case.
        This method determines which graph to build (basic or advanced) 
        based on the provided use case string. It initializes the graph 
        builder and constructs the appropriate graph.
        """
        if usecase == "Basic Chatbot": 
            self.basic_chatbot_build_graph()
        if usecase == "Chatbot with Tools":
            self.chatbot_with_tools_build_graph() 
        if usecase == "Travel Planner":
            self.build_travel_itinerary_graph()
            print("Graph built successfully for Travel Planner.")
        return self.graph_builder.compile()
    

