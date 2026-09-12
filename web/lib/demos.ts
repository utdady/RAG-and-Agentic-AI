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
  /** Homepage featured strip — omit from category grids when set. */
  featured?: {
    blurb: string;
    tags?: string[];
  };
  /** Orientation panel: dataset blurb, schema peek, starter prompts. */
  guide?: {
    blurb: string;
    tables: { name: string; columns: string[] }[];
    starters: string[];
  };
};

/** Featured hub cards, in display order. */
export const FEATURED_SLUGS = [
  "sql-agent",
  "docchat",
  "meal-planner",
] as const;

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
    featured: {
      blurb:
        "Ask Chinook SQLite questions in plain English — agent writes, runs, and self-corrects SQL.",
      tags: ["LangGraph", "Text-to-SQL", "Groq"],
    },
    guide: {
      blurb:
        "Chinook is a sample digital music store: artists release albums of tracks; customers place invoices. Use the schema below, then pick a starter or ask your own question.",
      tables: [
        {
          name: "Artist",
          columns: ["ArtistId", "Name"],
        },
        {
          name: "Album",
          columns: ["AlbumId", "Title", "ArtistId"],
        },
        {
          name: "Track",
          columns: [
            "TrackId",
            "Name",
            "AlbumId",
            "GenreId",
            "Composer",
            "Milliseconds",
            "UnitPrice",
          ],
        },
        {
          name: "Genre",
          columns: ["GenreId", "Name"],
        },
        {
          name: "Customer",
          columns: [
            "CustomerId",
            "FirstName",
            "LastName",
            "Country",
            "Email",
          ],
        },
        {
          name: "Invoice",
          columns: ["InvoiceId", "CustomerId", "InvoiceDate", "Total"],
        },
        {
          name: "InvoiceLine",
          columns: ["InvoiceLineId", "InvoiceId", "TrackId", "UnitPrice", "Quantity"],
        },
      ],
      starters: [
        "How many albums are in the database?",
        "List the top 5 artists by number of tracks",
        "Which customer spent the most?",
        "How many tracks are in the Rock genre?",
        "What are the 10 most expensive tracks?",
      ],
    },
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
      "Attach one or more PDF, DOCX, TXT, or MD files, then ask a question about them. DocChat indexes your uploads, checks whether the question can be answered, drafts a response, and verifies it against the sources — re-researching if needed.",
    tips: [
      "Attach files and type a clear question — both are required to run.",
      "Reference sections, tables, or topics by name when you can.",
      "If the answer is thin, narrow the question or ask about a specific document.",
    ],
    phase: 2,
    kind: "docs",
    github: "DocChat",
    tags: ["LangGraph", "RAG"],
    placeholder: "Ask a question about the uploaded files…",
    featured: {
      blurb:
        "Relevance-check → research → verify pipeline over your own documents, not a single-shot answer.",
      tags: ["Agentic RAG", "Self-verify"],
    },
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
    tagline: "Practice outreach from a LinkedIn-style profile.",
    description:
      "Cascade: ProxyCurl LinkedIn URL (if API key is set) → pasted profile text → bundled mock sample. Ask for icebreakers, talking points, or questions tailored to that person's background.",
    tips: [
      "Paste a LinkedIn URL only if the API has PROXYCURL_API_KEY; otherwise paste About/Experience text or leave blank for the mock profile.",
      "First run loads the profile — ask a concrete question next if the first reply is just setup facts.",
      "Ask for icebreakers, email openers, or talking points for a specific role or industry angle.",
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
      "Use the dataset panel below to scan columns, then pick a starter or ask your own chart/stat question.",
      "Name the column or outcome you care about (e.g. G3, studytime, absences) and the chart type you want.",
      "One task per message works best — e.g. a single bar chart or scatter, not three plots at once.",
    ],
    phase: 3,
    kind: "chat",
    github: "Data%20Viz%20Agent",
    tags: ["pandas", "matplotlib"],
    placeholder: "Plot average G3 by study time",
    guide: {
      blurb:
        "student-mat is a UCI sample of Portuguese secondary students in math class (~395 rows). Grades G1–G3 are period/final marks; lifestyle and family fields are mostly coded categories (often 1–5). Explore columns below, then try a starter or ask for a chart.",
      tables: [
        {
          name: "Outcomes",
          columns: ["G1", "G2", "G3", "failures", "absences"],
        },
        {
          name: "Study & school",
          columns: [
            "school",
            "studytime",
            "traveltime",
            "schoolsup",
            "paid",
            "activities",
            "higher",
            "reason",
          ],
        },
        {
          name: "Family & background",
          columns: [
            "sex",
            "age",
            "address",
            "famsize",
            "Pstatus",
            "Medu",
            "Fedu",
            "Mjob",
            "Fjob",
            "guardian",
            "famsup",
            "famrel",
          ],
        },
        {
          name: "Lifestyle",
          columns: [
            "internet",
            "romantic",
            "freetime",
            "goout",
            "Dalc",
            "Walc",
            "health",
            "nursery",
          ],
        },
      ],
      starters: [
        "How many rows are in this dataset?",
        "Generate a bar chart of gender (sex) counts",
        "Create a box plot of freetime vs G3",
        "Scatter plot absences vs G3",
        "Bar chart of average G3 for internet yes vs no",
        "Pie chart of average Walc by sex",
      ],
    },
  },
  {
    slug: "data-analysis",
    title: "AI Powered Data Analysis",
    tagline: "LangGraph agent over bundled CSVs.",
    description:
      "Explore bundled CSV files (classification and regression datasets) with natural language. The agent lists files, inspects columns, and can train simple models to evaluate targets.",
    tips: [
      "Use the dataset panel to see both CSVs, then pick a starter or ask your own question.",
      "Explore schema or a head sample before asking for model metrics.",
      "Both files use a column named target — say “evaluate … with target” when you want accuracy or R²/MSE.",
    ],
    phase: 3,
    kind: "chat",
    github: "AI%20Powered%20Data%20Analysis",
    tags: ["LangGraph", "pandas"],
    placeholder: "What CSV files are available?",
    guide: {
      blurb:
        "Two bundled CSVs: a binary classification set (breast-cancer–style cell measurements, target 0/1) and a regression set (California housing features, continuous target). The agent can summarize columns and run a quick RandomForest eval.",
      tables: [
        {
          name: "classification-dataset.csv",
          columns: [
            "target",
            "mean radius",
            "mean texture",
            "mean perimeter",
            "mean area",
            "mean smoothness",
            "mean compactness",
            "mean concavity",
            "mean concave points",
            "mean symmetry",
            "mean fractal dimension",
            "radius error",
            "texture error",
            "perimeter error",
            "area error",
            "smoothness error",
            "compactness error",
            "concavity error",
            "concave points error",
            "symmetry error",
            "fractal dimension error",
            "worst radius",
            "worst texture",
            "worst perimeter",
            "worst area",
            "worst smoothness",
            "worst compactness",
            "worst concavity",
            "worst concave points",
            "worst symmetry",
            "worst fractal dimension",
          ],
        },
        {
          name: "regression-dataset.csv",
          columns: [
            "MedInc",
            "HouseAge",
            "AveRooms",
            "AveBedrms",
            "Population",
            "AveOccup",
            "Latitude",
            "Longitude",
            "target",
          ],
        },
      ],
      starters: [
        "What CSV files are available?",
        "Summarize both datasets and say which is classification vs regression.",
        "Show the head of classification-dataset.csv",
        "Evaluate the classification dataset using target",
        "Evaluate the regression dataset and report R² and MSE",
      ],
    },
  },
  {
    slug: "style-finder",
    title: "Style Finder",
    tagline: "Match an outfit photo to a fashion catalog.",
    description:
      "Paste or attach a photo of an outfit. The vision pipeline embeds the image and finds the closest matches in a fashion catalog, showing similar styles and items.",
    tips: [
      "Use a clear, well-lit photo with the outfit fully visible.",
      "Paste an image into the prompt (Ctrl/Cmd+V) or use the paperclip — a message is optional, or ask “find similar items.”",
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
      "Paste or attach the meal photo first, then ask about calories, protein, or healthier swaps.",
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
      "Paste or attach a clear photo of the dish or ingredients, then send.",
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
    featured: {
      blurb:
        "Three-agent CrewAI workflow: plan a week of meals, build the shopping list, and stay in budget.",
      tags: ["CrewAI", "Multi-agent", "Tool use"],
    },
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

export function isFeaturedSlug(slug: string) {
  return (FEATURED_SLUGS as readonly string[]).includes(slug);
}
