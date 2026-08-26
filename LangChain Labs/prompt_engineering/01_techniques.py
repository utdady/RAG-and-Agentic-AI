"""01 — Prompt techniques: zero / one / few-shot, CoT, self-consistency."""

from __future__ import annotations

from _bootstrap import ask, banner
from shared.llm import get_chat_llm, get_llm_info

banner("01 Prompt techniques")
_, info = get_llm_info(temperature=0.5)
print(f"Using {info.provider}:{info.model}\n")

# Focused / creative demos use separate temps (Watsonx params → temperature only)
focused = get_chat_llm(temperature=0.2)
creative = get_chat_llm(temperature=0.5)

print("--- completion-style prompts ---")
for prompt in [
    "The wind is ",
    "The future of artificial intelligence is",
    "Once upon a time in a distant galaxy",
    "The benefits of sustainable energy include",
]:
    print(f"\nprompt: {prompt!r}")
    print(f"response: {ask(creative, prompt)}")

print("\n--- zero-shot: true/false ---")
zf = """Classify the following statement as true or false:
'The Eiffel Tower is located in Berlin.'

Answer:"""
print(ask(focused, zf))

print("\n--- zero-shot: movie / summarize / translate ---")
zero_shots = {
    "movie_review": """
Classify the following movie review as either 'positive' or 'negative'.

Review: "I was extremely disappointed by this film. The plot was predictable,
the acting was wooden, and the special effects looked cheap. I can't recommend
this to anyone."

Classification:
""",
    "climate_change": """
Summarize the following paragraph about climate change in no more than two sentences.

Paragraph: "Climate change refers to long-term shifts in temperatures and weather
patterns. These shifts may be natural, but since the 1800s, human activities have
been the main driver of climate change, primarily due to the burning of fossil
fuels like coal, oil and gas, which produces heat-trapping gases. The consequences
of climate change include more frequent and severe droughts, storms, and heat waves,
rising sea levels, melting glaciers, and warming oceans which can directly impact
biodiversity, agriculture, and human health."

Summary:
""",
    "translation": """
Translate the following English phrase into Spanish.

English: "I would like to order a coffee with milk and two sugars, please."

Spanish:
""",
}
for name, prompt in zero_shots.items():
    print(f"\n=== {name.upper()} ===")
    print(ask(focused, prompt))

print("\n--- one-shot: EN→FR ---")
one_shot_fr = """Here is an example of translating a sentence from English to French:

English: "How is the weather today?"
French: "Comment est le temps aujourd'hui?"

Now, translate the following sentence from English to French:

English: "Where is the nearest supermarket?"
"""
print(ask(focused, one_shot_fr))

print("\n--- one-shot: email / ML explanation / keywords ---")
one_shots = {
    "formal_email": """
Here is an example of a formal email requesting information:

Subject: Inquiry Regarding Product Specifications for Model XYZ-100

Dear Customer Support Team,

I hope this email finds you well. I am writing to request detailed specifications
for your product Model XYZ-100. Specifically, I am interested in learning about
its dimensions, power requirements, and compatibility with third-party accessories.

Could you please provide this information at your earliest convenience?
Additionally, I would appreciate any available documentation or user manuals
that you could share.

Thank you for your assistance in this matter.

Sincerely,
John Smith

---

Now, please write a formal email to a university admissions office requesting
information about their application deadline and required documents for the
Master's program in Computer Science:
""",
    "technical_concept": """
Here is an example of explaining a technical concept in simple terms:

Technical Concept: Blockchain
Simple Explanation: A blockchain is like a digital notebook that many people have
copies of. When someone writes a new entry in this notebook, everyone's copy gets
updated. Once something is written, it can't be erased or changed, and everyone
can see who wrote what. This makes it useful for recording important information
that needs to be secure and trusted by everyone.

---

Now, please explain the following technical concept in simple terms:

Technical Concept: Machine Learning
Simple Explanation:
""",
    "keyword_extraction": """
Here is an example of extracting keywords from a sentence:

Sentence: "Cloud computing offers businesses flexibility, scalability, and
cost-efficiency for their IT infrastructure needs."
Keywords: cloud computing, flexibility, scalability, cost-efficiency, IT infrastructure

---

Now, please extract the main keywords from the following sentence:

Sentence: "Sustainable agriculture practices focus on biodiversity, soil health,
water conservation, and reducing chemical inputs."
Keywords:
""",
}
for name, prompt in one_shots.items():
    print(f"\n=== {name.upper()} ===")
    print(ask(focused, prompt))

print("\n--- few-shot: emotion ---")
few_shot = """Here are few examples of classifying emotions in statements:

Statement: 'I just won my first marathon!'
Emotion: Joy

Statement: 'I can't believe I lost my keys again.'
Emotion: Frustration

Statement: 'My best friend is moving to another country.'
Emotion: Sadness

Now, classify the emotion in the following statement:
Statement: 'That movie was so scary I had to cover my eyes.'
Emotion:
"""
print(ask(focused, few_shot))

print("\n--- chain-of-thought ---")
cot = """Consider the problem: 'A store had 22 apples. They sold 15 apples today
and got a new delivery of 8 apples. How many apples are there now?'

Break down each step of your calculation.
"""
print(ask(creative, cot))

print("\n--- self-consistency style ---")
sc = """When I was 6, my sister was half of my age. Now I am 70, what age is my sister?

Provide three independent calculations and explanations, then determine the most
consistent result.
"""
print(ask(creative, sc))
