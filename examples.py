"""
Example: Using Chat Website API Wrapper with CrewAI

This demonstrates how to use the local chat API server as the LLM for CrewAI.
"""
import os

# Set dummy API key for local server (required by CrewAI)
os.environ["OPENAI_API_KEY"] = "not-needed"
os.environ["OPENAI_API_BASE"] = "http://127.0.0.1:8000/v1"

# Example 1: Basic CrewAI Setup
def example_crewai_basic():
    """Basic CrewAI setup using local chat server"""
    
    try:
        from crewai import Agent, Task, Crew, LLM
    except ImportError:
        print("Please install CrewAI: pip install crewai crewai-tools")
        return
    
    # Configure LLM to point to local server
    llm = LLM(
        model="gpt-4",
        base_url="http://127.0.0.1:8000/v1",
        api_key="not-needed"
    )
    
    # Create agents using local chat server as LLM
    researcher = Agent(
        role="Researcher",
        goal="Research topics thoroughly",
        backstory="You are a thorough research expert",
        llm=llm
    )
    
    analyst = Agent(
        role="Analyst",
        goal="Analyze information and provide insights",
        backstory="You are an expert analyst",
        llm=llm
    )
    
    # Create tasks
    research_task = Task(
        description="Research the latest trends in AI/ML",
        expected_output="A summary of recent AI/ML trends",
        agent=researcher
    )
    
    analysis_task = Task(
        description="Analyze the research findings and provide insights",
        expected_output="Key insights from the research",
        agent=analyst
    )
    
    # Create crew and execute
    crew = Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        verbose=True
    )
    
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("CREW RESULT:")
    print("=" * 60)
    print(result)


# Example 2: Using local chat server with LangGraph
def example_langgraph():
    """Example using local chat server with LangGraph"""
    
    try:
        from langgraph.graph import StateGraph, END
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage
        from typing import TypedDict, List
    except ImportError:
        print("Please install LangGraph: pip install langgraph langchain-openai")
        return
    
    # Create LLM pointing to local server
    llm = ChatOpenAI(
        model="gpt-4",
        base_url="http://127.0.0.1:8000/v1",
        api_key="not-needed",
        temperature=0.7
    )
    
    # Define state
    class GraphState(TypedDict):
        messages: List[str]
        current_topic: str
    
    # Define nodes
    def research_node(state: GraphState) -> GraphState:
        """Research node"""
        topic = state.get("current_topic", "AI")
        response = llm.invoke([
            HumanMessage(content=f"Research and summarize: {topic}")
        ])
        state["messages"].append(f"Research: {response.content}")
        return state
    
    def analysis_node(state: GraphState) -> GraphState:
        """Analysis node"""
        last_message = state["messages"][-1] if state["messages"] else ""
        response = llm.invoke([
            HumanMessage(content=f"Analyze this: {last_message}")
        ])
        state["messages"].append(f"Analysis: {response.content}")
        return state
    
    # Create graph
    workflow = StateGraph(GraphState)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", END)
    
    # Compile and run
    app = workflow.compile()
    
    result = app.invoke({
        "messages": [],
        "current_topic": "Artificial Intelligence"
    })
    
    print("\n" + "=" * 60)
    print("LANGGRAPH RESULT:")
    print("=" * 60)
    for msg in result["messages"]:
        print(msg)


# Example 3: Simple direct usage
def example_simple():
    """Simple direct usage without CrewAI/LangGraph"""
    
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage
    
    # Create LLM pointing to local server
    llm = ChatOpenAI(
        model="gpt-4",
        base_url="http://127.0.0.1:8000/v1",
        api_key="not-needed",
        temperature=0.7
    )
    
    # Use it
    response = llm.invoke([
        HumanMessage(content="What is artificial intelligence?")
    ])
    
    print("\n" + "=" * 60)
    print("RESPONSE:")
    print("=" * 60)
    print(response.content)


# Example 4: Multi-agent collaboration
def example_multiagent():
    """Multi-agent collaboration example"""
    
    try:
        from crewai import Agent, Task, Crew, LLM
    except ImportError:
        print("Please install CrewAI: pip install crewai crewai-tools")
        return
    
    llm = LLM(
        model="gpt-4",
        base_url="http://127.0.0.1:8000/v1",
        api_key="not-needed"
    )
    
    # Create specialized agents
    cto = Agent(
        role="CTO",
        goal="Provide technical architecture recommendations",
        backstory="You are an experienced Chief Technology Officer",
        llm=llm
    )
    
    product_lead = Agent(
        role="Product Lead",
        goal="Define product requirements and strategy",
        backstory="You are an experienced product strategy expert",
        llm=llm
    )
    
    # Define their collaboration tasks
    architecture_task = Task(
        description="Design a scalable architecture for an AI platform",
        expected_output="Technical architecture document",
        agent=cto
    )
    
    product_task = Task(
        description="Define product roadmap based on the technical architecture",
        expected_output="Product roadmap and strategy",
        agent=product_lead
    )
    
    # Run collaboration
    crew = Crew(
        agents=[cto, product_lead],
        tasks=[architecture_task, product_task],
        verbose=True
    )
    
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("COLLABORATION RESULT:")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("Chat Website API Wrapper - CrewAI/LangGraph Examples")
    print("=" * 60)
    
    print("""
Available examples:
1. Basic CrewAI setup
2. LangGraph workflow
3. Simple direct usage (no frameworks)
4. Multi-agent collaboration

Make sure the server is running:
    python run.py

Then run an example:
    python examples.py --example 1
""")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        example_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        
        if example_num == 1:
            print("\n[Running] Example 1: Basic CrewAI")
            example_crewai_basic()
        elif example_num == 2:
            print("\n[Running] Example 2: LangGraph")
            example_langgraph()
        elif example_num == 3:
            print("\n[Running] Example 3: Simple Usage")
            example_simple()
        elif example_num == 4:
            print("\n[Running] Example 4: Multi-agent")
            example_multiagent()
    else:
        print("\nStart the server first: python run.py")
        print("Then try: python examples.py --example 1")
