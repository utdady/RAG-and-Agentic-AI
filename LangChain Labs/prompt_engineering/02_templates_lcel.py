"""02 — PromptTemplate + LCEL task chains (joke, summarize, QA, classify, SQL, roleplay)."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from _bootstrap import banner
from shared.llm import get_llm_info

banner("02 PromptTemplate + LCEL")
llm, _ = get_llm_info(temperature=0.5)
parser = StrOutputParser()


def make_chain(template: str):
    """prompt | llm | parser — no RunnableLambda needed with Chat models."""
    return PromptTemplate.from_template(template) | llm | parser


print("--- joke ---")
joke = make_chain("Tell me a {adjective} joke about {content}.")
print(joke.invoke({"adjective": "funny", "content": "chickens"}))
print(joke.invoke({"adjective": "sad", "content": "fish"}))

print("\n--- summarize ---")
tech_blurb = """
The rapid advancement of technology in the 21st century has transformed various
industries, including healthcare, education, and transportation. Innovations such
as artificial intelligence, machine learning, and the Internet of Things have
revolutionized how we approach everyday tasks and complex problems. For instance,
AI-powered diagnostic tools are improving the accuracy and speed of medical
diagnoses, while smart transportation systems are making cities more efficient
and reducing traffic congestion. Moreover, online learning platforms are making
education more accessible to people around the world, breaking down geographical
and financial barriers. These technological developments are not only enhancing
productivity but also contributing to a more interconnected and informed society.
"""
summarize = make_chain("Summarize the {content} in one sentence.")
print(summarize.invoke({"content": tech_blurb}))

print("\n--- grounded QA ---")
solar = """
The solar system consists of the Sun, eight planets, their moons, dwarf planets,
and smaller objects like asteroids and comets. The inner planets—Mercury, Venus,
Earth, and Mars—are rocky and solid. The outer planets—Jupiter, Saturn, Uranus,
and Neptune—are much larger and gaseous.
"""
qa = make_chain(
    """Answer the {question} based on the {content}.
Respond "Unsure about answer" if not sure about the answer.

Answer:"""
)
print(
    qa.invoke(
        {
            "question": "Which planets in the solar system are rocky and solid?",
            "content": solar,
        }
    )
)

print("\n--- classify ---")
classify = make_chain(
    """Classify the {text} into one of the {categories}.

Category:"""
)
print(
    classify.invoke(
        {
            "text": (
                "The concert last night was an exhilarating experience with "
                "outstanding performances by all artists."
            ),
            "categories": "Entertainment, Food and Dining, Technology, Literature, Music.",
        }
    )
)

print("\n--- SQL generation (demo only — do not run against a DB) ---")
sql = make_chain(
    """Generate an SQL query based on the {description}

SQL Query:"""
)
print(
    sql.invoke(
        {
            "description": (
                "Retrieve the names and email addresses of all customers from the "
                "'customers' table who have made a purchase in the last 30 days. "
                "The table 'purchases' contains a column 'purchase_date'."
            )
        }
    )
)

print("\n--- roleplay (single-shot; original lab used an interactive loop) ---")
roleplay = make_chain(
    """You are an expert {role}. I have this question {question}.
I would like our conversation to be {tone}.

Answer:"""
)
print(
    roleplay.invoke(
        {
            "role": "Dungeon & Dragons game master",
            "question": "We enter a mossy cave. What do we see?",
            "tone": "engaging and immersive",
        }
    )
)
print(
    "\nTip: for an interactive loop, wrap roleplay.invoke in a while True / input() "
    "and exit on quit/exit/bye."
)
