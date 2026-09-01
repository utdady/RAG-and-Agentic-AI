export type DemoKind =
  | "chat"
  | "pdf"
  | "docs"
  | "youtube"
  | "image"
  | "audio"
  | "form"
  | "compare"
  | "healthcare";

export type Demo = {
  slug: string;
  title: string;
  tagline: string;
  description?: string;
  tips?: string[];
  phase: number;
  kind: DemoKind;
  github: string;
  tags: string[];
  placeholder?: string;
};

export const GITHUB_BASE =
  "https://github.com/utdady/RAG-and-Agentic-AI/tree/main";

export const DEMOS: Demo[] = [
  {
    slug: "pdf-qa",
    title: "PDF QA Bot",
    tagline: "Upload a PDF and ask grounded questions.",
    description:
      "Attach a PDF, then ask questions in plain English. Answers are grounded in the document using vector search over chunked text — good for reports, papers, or manuals.",
    tips: [
      "Attach the PDF first, then ask your question — the file must be uploaded before each run.",
      "Ask about specific sections, figures, or claims rather than broad summaries.",
      "Follow up with “where does it say that?” or “summarize section 2” to drill into details.",
    ],
    phase: 1,
    kind: "pdf",
    github: "PDF%20QA%20Bot",
    tags: ["RAG", "Chroma"],
    placeholder: "What is this document about?",
  },
  {
    slug: "sql-agent",
    title: "Natural Language SQL Agent",
    tagline: "Ask Chinook SQLite questions in English.",
    description:
      "Type a question about the bundled Chinook music store database. The agent translates it to SQL, runs the query, and returns a readable answer.",
    tips: [
      "Ask one clear question at a time — counts, lists, or comparisons work best.",
      "Name tables or concepts when you know them (artists, albums, invoices, customers).",
      "Try “how many…”, “list the top 5…”, or “which customer spent the most?”",
    ],
    phase: 1,
    kind: "chat",
    github: "Natural%20Language%20SQL%20Agent",
    tags: ["SQL", "LangChain"],
    placeholder: "How many albums are in the database?",
  },
  {
    slug: "math-assistant",
    title: "AI Math Assistant",
    tagline: "ReAct math agent with Wikipedia tools.",
    description:
      "Ask math questions step by step. The agent can call Wikipedia and calculator tools, show its reasoning, and revise when a step looks wrong.",
    tips: [
      "State the full problem in one message — include variables, constraints, and what you want solved.",
      "Ask for step-by-step work when you want to see the reasoning, not just the final number.",
      "If the answer looks off, ask it to recheck a specific step.",
    ],
    phase: 1,
    kind: "chat",
    github: "AI%20Math%20Assistant",
    tags: ["LangGraph", "Tools"],
    placeholder: "What is the derivative of x^3?",
  },
  {
    slug: "youtube-summarizer",
    title: "YouTube Summarizer",
    tagline: "Transcript → RAG summary and Q&A.",
    description:
      "Paste a YouTube URL to fetch the transcript, build a search index, and get a summary. Add an optional follow-up question to dig into specific moments or claims.",
    tips: [
      "Paste the full YouTube URL in the field above the chat, then run.",
      "Leave the message blank for a general summary, or ask something specific like “what did they say about X?”",
      "Follow-ups work best when they reference a topic or quote from the video.",
    ],
    phase: 1,
    kind: "youtube",
    github: "YouTube%20Summarizer",
    tags: ["RAG", "FAISS"],
    placeholder: "Optional follow-up question…",
  },
  {
    slug: "connoisseur",
    title: "Connoisseur Companion",
    tagline: "Multi-agent California dining recommendations.",
    description:
      "Describe the kind of meal or night out you want — location, vibe, dietary needs, budget. Several agents build a profile, search a dining knowledge base, and synthesize restaurant and recipe picks.",
    tips: [
      "Include city or neighborhood, occasion, cuisine preferences, and any dietary restrictions.",
      "Mention vibe (casual, date night, group) and budget if it matters.",
      "One rich prompt beats several vague ones — e.g. “Vegetarian date night in SF, lively, mid-range.”",
    ],
    phase: 2,
    kind: "chat",
    github: "Connoisseur%20Companion",
    tags: ["Multi-agent", "RAG", "MCP"],
    placeholder: "Date night in SF, vegetarian, lively vibe…",
  },
  {
    slug: "docchat",
    title: "DocChat",
    tagline: "Relevance → research → verify over your docs.",
    description:
      "Attach one or more PDF, DOCX, TXT, or MD files, then ask a question about them. DocChat indexes your uploads with hybrid search (keyword + semantic), checks whether the question can be answered, drafts a response, and verifies it against the sources — re-researching if needed.",
    tips: [
      "Attach all relevant files first, then ask a focused question about their content.",
      "Reference sections, tables, or topics by name when you can.",
      "If the answer is thin, narrow the question or ask about a specific document.",
    ],
    phase: 2,
    kind: "docs",
    github: "DocChat",
    tags: ["LangGraph", "RAG"],
    placeholder: "Ask a question about the uploaded files…",
  },
  {
    slug: "food-search",
    title: "Food Search RAG",
    tagline: "Chroma food retrieval plus LLM recommendations.",
    description:
      "Describe what you are in the mood for — cuisine, calories, spice level, ingredients. The app retrieves similar dishes from a food catalog and turns the matches into a tailored recommendation.",
    tips: [
      "Combine constraints in one message: cuisine, calories, spice, health goals, or ingredients to avoid.",
      "Be specific — “spicy Thai under 500 calories” works better than “something healthy.”",
      "Ask for alternatives or variations in a follow-up if the first suggestion isn’t quite right.",
    ],
    phase: 2,
    kind: "chat",
    github: "Food%20Search%20RAG",
    tags: ["RAG", "Chroma"],
    placeholder: "Spicy healthy dinner under 400 calories",
  },
  {
    slug: "icebreaker",
    title: "Icebreaker Bot",
    tagline: "Chat with a mock LinkedIn profile (RAG).",
    description:
      "Loads a mock professional profile into memory, then lets you practice outreach. Ask for icebreakers, talking points, or questions tailored to that person's background.",
    tips: [
      "First run loads the profile — ask a concrete question on the next message if the first reply is just setup.",
      "Ask for icebreakers, email openers, or talking points for a specific role or industry angle.",
      "Request shorter or more formal versions if you want to tune the tone.",
    ],
    phase: 2,
    kind: "chat",
    github: "Icebreaker%20Bot",
    tags: ["LlamaIndex", "RAG"],
    placeholder: "What should I mention as an icebreaker?",
  },
  {
    slug: "data-viz",
    title: "Data Viz Agent",
    tagline: "Pandas + matplotlib over student-mat.",
    description:
      "Ask for charts or stats on the bundled student-mat dataset (grades, study time, absences, and more). The agent writes pandas code, runs it, and returns plots or summaries — no need to upload files.",
    tips: [
      "Name the column or outcome you care about (e.g. G3, studytime, absences) and the chart type you want.",
      "Try “plot average G3 by study time” or “histogram of absences” — one task per message works best.",
      "Ask for a table or summary first if you’re not sure which columns exist.",
    ],
    phase: 3,
    kind: "chat",
    github: "Data%20Viz%20Agent",
    tags: ["pandas", "matplotlib"],
    placeholder: "Plot average G3 by study time",
  },
  {
    slug: "data-analysis",
    title: "AI Powered Data Analysis",
    tagline: "LangGraph agent over bundled CSVs.",
    description:
      "Explore bundled CSV files (classification and regression datasets) with natural language. The agent lists files, inspects columns, and can train simple models to evaluate targets.",
    tips: [
      "Start with “what CSV files are available?” or “summarize the columns in classification-dataset.csv.”",
      "Ask one analysis step at a time — explore schema before asking for model accuracy.",
      "Name the target column when requesting classification or regression (e.g. “evaluate churn as the target”).",
    ],
    phase: 3,
    kind: "chat",
    github: "AI%20Powered%20Data%20Analysis",
    tags: ["LangGraph", "pandas"],
    placeholder: "What CSV files are available?",
  },
  {
    slug: "style-finder",
    title: "Style Finder",
    tagline: "Match an outfit photo to a fashion catalog.",
    description:
      "Attach a photo of an outfit. The vision pipeline embeds the image and finds the closest matches in a fashion catalog, showing similar styles and items.",
    tips: [
      "Use a clear, well-lit photo with the outfit fully visible.",
      "Attach the image with the paperclip, then send — a message is optional but you can ask “find similar items.”",
      "Try different angles or crop to the outfit if matches seem off.",
    ],
    phase: 3,
    kind: "image",
    github: "Style%20Finder",
    tags: ["Vision", "ResNet"],
  },
  {
    slug: "nutrition-coach",
    title: "AI Nutrition Coach",
    tagline: "Vision LLM calorie and nutrition notes.",
    description:
      "Attach a meal photo and ask about calories, macros, or healthier swaps. The vision model describes what it sees and gives practical nutrition notes.",
    tips: [
      "Attach the photo first, then ask a specific question — calories, protein, or healthier swaps.",
      "Mention portion size or ingredients if they’re not obvious in the image.",
      "Treat output as rough guidance, not medical or dietary advice.",
    ],
    phase: 3,
    kind: "image",
    github: "AI%20Nutrition%20Coach",
    tags: ["Vision"],
    placeholder: "How many calories are in this meal?",
  },
  {
    slug: "model-compare",
    title: "Model Comparison Chat",
    tagline: "Three Groq slots, structured JSON replies.",
    description:
      "Send the same prompt to three model slots and compare structured JSON responses side by side — useful for tone, format, and instruction-following differences.",
    tips: [
      "Give clear instructions in the prompt — tone, length, format, and audience.",
      "Use tasks with a definite answer shape, e.g. “polite decline email in JSON with subject and body.”",
      "Compare how each slot handles constraints; re-run with tighter instructions to see differences.",
    ],
    phase: 3,
    kind: "compare",
    github: "Model%20Comparison%20Chat",
    tags: ["Groq", "JSON"],
    placeholder: "Write a polite reply declining a meeting…",
  },
  {
    slug: "nourishbot",
    title: "NourishBot",
    tagline: "CrewAI recipe or nutrition analysis from a photo.",
    description:
      "Attach a food photo and pick a workflow: generate a recipe from what you see, or run a nutrition analysis. A CrewAI team coordinates vision and writing steps.",
    tips: [
      "Choose recipe or analysis from the dropdown before you run.",
      "Attach a clear photo of the dish or ingredients, then send.",
      "For recipes, mention servings or dietary needs in your message.",
    ],
    phase: 4,
    kind: "image",
    github: "NourishBot",
    tags: ["CrewAI", "Vision"],
  },
  {
    slug: "meal-planner",
    title: "Meal Grocery Planner",
    tagline: "CrewAI meal plan, shopping list, budget.",
    description:
      "Fill in meal preferences, servings, budget, and dietary restrictions. The crew produces a meal plan, grocery list, and cost-aware shopping guidance.",
    tips: [
      "Fill all form fields — meal name, servings, budget, and dietary notes — before submitting.",
      "Be specific on diet (vegan, gluten-free) and skill level for realistic plans.",
      "Adjust servings or budget and run again to compare options.",
    ],
    phase: 4,
    kind: "form",
    github: "Meal%20Grocery%20Planner",
    tags: ["CrewAI"],
  },
  {
    slug: "healthcare",
    title: "Healthcare Chatbot",
    tagline: "Educational multi-agent consult — not medical care.",
    description:
      "Describe symptoms or how you are feeling in plain language. Multiple educational agents discuss possibilities — for learning only, not diagnosis or treatment.",
    tips: [
      "Pick symptom or mental-health mode from the dropdown, then describe what you’re experiencing.",
      "Include duration, severity, and context — not just a single keyword.",
      "Use for educational exploration only; not a substitute for professional care.",
    ],
    phase: 4,
    kind: "healthcare",
    github: "Healthcare%20Chatbot",
    tags: ["AutoGen", "Educational"],
    placeholder: "Describe symptoms or feelings (educational only)…",
  },
  {
    slug: "meeting-assistant",
    title: "Meeting Assistant",
    tagline: "Whisper-tiny transcript → minutes and tasks.",
    description:
      "Attach an audio recording of a meeting. Whisper transcribes it, then the app drafts minutes, decisions, and action items you can review or ask follow-ups about.",
    tips: [
      "Attach a clear audio file (MP3, WAV, M4A) — shorter clips process faster.",
      "After the summary, ask follow-ups like “list action items” or “who said what about the deadline?”",
      "Good audio quality improves transcript accuracy.",
    ],
    phase: 5,
    kind: "audio",
    github: "Meeting%20Assistant",
    tags: ["Whisper", "Groq"],
  },
];

export type DemoGroup = {
  id: string;
  label: string;
  slugs: string[];
};

export const DEMO_GROUPS: DemoGroup[] = [
  {
    id: "rag",
    label: "RAG & Chat",
    slugs: ["pdf-qa", "sql-agent", "math-assistant", "youtube-summarizer"],
  },
  {
    id: "agents",
    label: "Agents & Tools",
    slugs: ["connoisseur", "docchat", "food-search", "icebreaker"],
  },
  {
    id: "data",
    label: "Data & Vision",
    slugs: [
      "data-viz",
      "data-analysis",
      "style-finder",
      "nutrition-coach",
      "model-compare",
    ],
  },
  {
    id: "crews",
    label: "Crew Workflows",
    slugs: ["nourishbot", "meal-planner", "healthcare"],
  },
  {
    id: "audio",
    label: "Audio",
    slugs: ["meeting-assistant"],
  },
];

export function demoBySlug(slug: string) {
  return DEMOS.find((d) => d.slug === slug);
}
