from dotenv import find_dotenv, load_dotenv
from google.adk import Agent  # type: ignore
from google.adk.models.lite_llm import LiteLlm  # type: ignore

load_dotenv(find_dotenv())

root_agent = Agent(
    name="anything_agent",
    model=LiteLlm("openrouter/openai/o3-mini"),
    description="Agent to answer questions.",
    instruction="I can answer your questions.",
    tools=[],
)
