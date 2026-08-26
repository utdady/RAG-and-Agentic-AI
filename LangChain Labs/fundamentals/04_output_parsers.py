"""04 — Output parsers (JSON / CSV / structured movie JSON)."""

from __future__ import annotations

from langchain_core.output_parsers import (
    CommaSeparatedListOutputParser,
    JsonOutputParser,
)
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from _bootstrap import banner
from shared.llm import get_llm_info

banner("04 Output parsers")
llm, _ = get_llm_info(temperature=0.1)

# --- CSV / list ---
csv_parser = CommaSeparatedListOutputParser()
csv_prompt = PromptTemplate.from_template(
    "List 5 programming languages related to data science.\n{format_instructions}"
)
print("--- CommaSeparatedListOutputParser ---")
raw = llm.invoke(
    csv_prompt.format(format_instructions=csv_parser.get_format_instructions())
).content
print("raw:", raw)
print("parsed:", csv_parser.parse(raw))


# --- JSON via Pydantic ---
class Movie(BaseModel):
    title: str = Field(description="movie title")
    year: int = Field(description="release year")
    genre: str = Field(description="primary genre")


json_parser = JsonOutputParser(pydantic_object=Movie)
json_prompt = PromptTemplate(
    template=(
        "Suggest one classic science-fiction movie.\n"
        "{format_instructions}\n"
        "Movie topic: {topic}"
    ),
    input_variables=["topic"],
    partial_variables={"format_instructions": json_parser.get_format_instructions()},
)
print("\n--- JsonOutputParser (Movie) ---")
raw = llm.invoke(json_prompt.format(topic="space travel")).content
print("raw:", raw)
print("parsed:", json_parser.parse(raw))
