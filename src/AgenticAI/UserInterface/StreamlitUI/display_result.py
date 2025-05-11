import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message
    
    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message

        if usecase == "Basic Chatbot":
            # Basic chatbot implementation
            for event in graph.stream({"messages": ("user", user_message)}):
                for value in event.values():
                    with st.chat_message("user"):
                        st.write(user_message)
                    with st.chat_message("assistant"):
                        st.write(value["messages"].content)

        elif usecase == "Chatbot with Tools":
            # Tool-enabled chatbot implementation
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            for message in res["messages"]:
                if isinstance(message, HumanMessage):
                    with st.chat_message("user"):
                        st.write(message.content)
                elif isinstance(message, ToolMessage):
                    with st.chat_message("AI"):
                        st.write("🔧 Tool Call Started")
                        st.json(message.content)
                        st.write("✅ Tool call completed")
                elif isinstance(message, AIMessage) and message.content:
                    with st.chat_message("assistant"):
                        st.markdown(message.content)

        elif usecase == "Travel Planner":
            initial_state = {"topic": user_message}
            
            # Handle greetings and non-travel queries
            if initial_state["topic"].lower() in {"hello", "hi", "hey", "hello!"}:
                st.markdown("👋 **Hello! I'm your AI Travel Assistant.** Let's plan your perfect trip!")
                st.markdown("""
                Try asking about: trips, itineraries, or travel plans.
                """)
                return

            # Display user query
            with st.chat_message("user"):
                st.markdown(f"✈️ **Planning trip to:** {user_message}")

            # Generate itinerary
            with st.spinner("🌍 Crafting your perfect itinerary..."):
                state = graph.invoke(initial_state)

            # Handle non-travel responses
            if "response" in state:
                with st.chat_message("assistant"):
                    st.markdown("🚨 **Travel Specialist Notice**")
                    st.markdown(state["response"])
                return

            # Display travel planning results
            with st.container():
                if "response" in state:
                    st.markdown("🚨 **Travel Specialist Notice**")
                    st.markdown(state["response"])
                    return
                # Itinerary structure
                if "sections" in state:
                    with st.expander("📋 Itinerary Blueprint", expanded=True):
                        cols = st.columns(3)
                        for idx, sec in enumerate(state["sections"], 1):
                            with cols[(idx-1)%3]:
                                st.markdown(f"""
                                ##### {idx}. {getattr(sec, 'name', 'Section')}
                                *{getattr(sec, 'description', '')[:60]}...*
                                """)
                                st.progress(min((idx/len(state["sections"]))*100, 100))

                # Draft content
                if "completed_sections" in state:
                    st.divider()
                    with st.expander("📄 Content Drafts", expanded=False):
                        tabs = st.tabs([f"Section {i+1}" for i in range(len(state["completed_sections"]))])
                        for idx, (tab, content) in enumerate(zip(tabs, state["completed_sections"])):
                            with tab:
                                st.markdown(f"### {state['sections'][idx].name}")
                                st.caption(f"Character count: {len(content)}")
                                st.markdown(content[:500] + "..." if len(content) > 500 else content)

                # Quality check status
                if "evaluator_passed" in state:
                    st.divider()
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.metric("Quality Check", "Passed ✅" if state["evaluator_passed"] else "Needs Fixing ❌")
                    with col2:
                        if state["evaluator_passed"]:
                            st.success("All sections meet our quality standards!")
                        else:
                            st.error("Some sections need improvement. Auto-correcting...")

                # Final output
                if "final_report" in state:
                    st.divider()
                    st.subheader("🌟 Final Travel Plan")
                    
                    if isinstance(state["final_report"], list):
                        for line in state["final_report"]:
                            st.markdown(line)
                    else:
                        # Enhanced markdown rendering with section splitting
                        sections = state["final_report"].split("\n\n---\n\n")
                        for section in sections:
                            st.markdown(section)
                            if "---" not in section:  # Add visual separator between sections
                                st.write("\n" + "-"*50 + "\n")
