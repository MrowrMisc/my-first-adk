from dotenv import find_dotenv, load_dotenv
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

load_dotenv(find_dotenv())


def get_users_name() -> str:
    """
    Get the user's name.
    """
    return "The user's name is Sally Smith the First."


root_agent = Agent(
    name="anything_agent",
    model=LiteLlm("openrouter/openai/o3-mini"),
    description="Agent to answer questions.",
    instruction="""
    I can answer your questions.
    """,
    tools=[get_users_name],
)
