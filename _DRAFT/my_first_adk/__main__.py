from typing import Any
from uuid import uuid4

from dotenv import find_dotenv, load_dotenv
from google.adk import Runner
from google.adk.sessions import DatabaseSessionService, Session
from google.genai import types

from .agent import my_first_agent

load_dotenv(find_dotenv())


def print_session(session: Session) -> None:
    print("Session ID:", session.id)
    for key, value in session.state.items():
        print(f"{key}: {value}")


def main():
    app_name = "my_first_adk"
    user_id = "mrowrpurr"
    session_id = str(uuid4())

    # session_service = InMemorySessionService()
    session_service = DatabaseSessionService(
        db_url="sqlite:///./my_first_adk_sessions.db",
    )
    initial_state: dict[str, Any] = {}

    session = session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state,
    )

    runner = Runner(
        agent=my_first_agent,
        app_name=app_name,
        session_service=session_service,
    )

    new_message = types.Content(
        role="user",
        parts=[
            types.Part(text="What is my name?"),
        ],
    )

    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final response: {event.content.parts[0].text}")

    print("What's in the session now?")
    print_session(session)


if __name__ == "__main__":
    main()
