from src.AgenticAI.State.state import State

class BasicChatbotNode:
    """
    A class representing a basic chatbot node in a graph.
    This class is responsible for processing user input and generating responses.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> State:
        """
        Processes the user input and generates a response using the LLM.
        """
        return {"messages" : self.llm.invoke(state['messages'])}