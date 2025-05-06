from src.AgenticAI.State.state import State

class ChatBotWithToolNode:
    """
    A class representing a chatbot node with tool capabilities in a graph.
    This class is responsible for processing user input, generating responses,
    and invoking tools as needed.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> State:
        """
        Processes the user input, generates a response using the LLM,
        and invokes tools if necessary.
        """
        user_input = state['messages'][-1] if state['messages'] else ""
        llm_response = self.llm.invoke([{"role": "user", "content": user_input}])

        tools_response = f"Tool integration for: '{user_input}'"

        return {
            "messages": [
                llm_response,
                tools_response
            ]
        }
    
    def create_chatbot(self, tools):
        """
        Creates a chatbot node with tool capabilities.
        This method initializes the chatbot node and sets up the necessary tools.
        """
        llm_wihh_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            """
            Chatbot logic for processing the input state and returning a response.
            """
            return {"messages": llm_wihh_tools.invoke(state['messages'])}
        return chatbot_node