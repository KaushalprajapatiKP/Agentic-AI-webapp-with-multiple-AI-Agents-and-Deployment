from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Retrieves a list of tools for the chatbot.
    This function currently includes a search tool (TavilySearchResults) 
    and can be extended to include more tools in the future.
    """
    tools = [
        TavilySearchResults(max_results=5),
        # Add more tools here as needed
    ]
    return tools

def create_tool_node(tools):
    """
    Creates a tool node for the chatbot.
    This function initializes a ToolNode with the provided tools and 
    sets up the necessary parameters for the node.
    """
    return ToolNode(tools=tools)
