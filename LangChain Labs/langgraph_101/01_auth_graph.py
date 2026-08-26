"""01 — Auth StateGraph: input → validate → success | failure.

Course used interactive input(); here credentials are passed in invoke().
"""

from __future__ import annotations

from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from _bootstrap import banner

banner("01 Auth graph")


class AuthState(TypedDict):
    username: Optional[str]
    password: Optional[str]
    is_authenticated: Optional[bool]
    output: Optional[str]


def input_node(state: AuthState) -> dict:
    # Non-interactive: keep existing username/password from invoke()
    username = (state.get("username") or "").strip()
    password = (state.get("password") or "").strip()
    print(f"[InputNode] username={username!r} password={'*' * len(password)}")
    return {"username": username, "password": password}


def validate_credentials_node(state: AuthState) -> dict:
    username = state.get("username") or ""
    password = state.get("password") or ""
    ok = username == "test_user" and password == "secure_password"
    print(f"[Validate] authenticated={ok}")
    return {"is_authenticated": ok}


def success_node(state: AuthState) -> dict:
    return {"output": "Authentication successful! Welcome."}


def failure_node(state: AuthState) -> dict:
    return {"output": "Not successful, please try again!"}


def router(state: AuthState) -> str:
    return "success_node" if state.get("is_authenticated") else "failure_node"


def build_app():
    workflow = StateGraph(AuthState)
    workflow.add_node("InputNode", input_node)
    workflow.add_node("ValidateCredential", validate_credentials_node)
    workflow.add_node("Success", success_node)
    workflow.add_node("Failure", failure_node)

    workflow.set_entry_point("InputNode")
    workflow.add_edge("InputNode", "ValidateCredential")
    workflow.add_conditional_edges(
        "ValidateCredential",
        router,
        {"success_node": "Success", "failure_node": "Failure"},
    )
    # Course looped Failure → InputNode; for demos we end after one attempt
    workflow.add_edge("Success", END)
    workflow.add_edge("Failure", END)
    return workflow.compile()


if __name__ == "__main__":
    app = build_app()

    print("\n--- fail ---")
    print(app.invoke({"username": "alice", "password": "wrong"}))

    print("\n--- success ---")
    print(app.invoke({"username": "test_user", "password": "secure_password"}))
