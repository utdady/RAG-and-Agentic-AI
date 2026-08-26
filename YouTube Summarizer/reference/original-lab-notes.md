# Original lab notes (reference)

Source: IBM Skills Network-style notebook  
("AI-Powered YouTube Summarizer, QA Tool with RAG, LangChain, FAISS").

**Not the runnable app** — uses Watsonx LLM + Slate embeddings.  
Working app: [`../app.py`](../app.py) (Groq/Ollama + local MiniLM + FAISS).

Code blocks cleaned for readability; logic matches the lab.

---

## 1. Install dependencies

```bash
pip install youtube-transcript-api==1.2.1
pip install faiss-cpu==1.8.0
pip install langchain==0.2.6
pip install langchain-community==0.2.6
pip install ibm-watsonx-ai==1.0.10
pip install langchain_ibm==0.1.8
pip install gradio==4.44.1

python3.11 -m pip uninstall -y huggingface_hub
python3.11 -m pip install huggingface_hub==0.16.4
pip install --upgrade gradio fastapi starlette jinja2
```

---

## 2. Imports

```python
import gradio as gr
import re
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from ibm_watsonx_ai.foundation_models.utils import get_embedding_model_specs
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
```

---

## 3. Extract video id

```python
def get_video_id(url):
    pattern = r"https:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = get_video_id(url)
print(video_id)  # dQw4w9WgXcQ
```

---

## 4. Fetch English transcript

```python
def get_transcript(url):
    video_id = get_video_id(url)
    ytt_api = YouTubeTranscriptApi()
    transcripts = ytt_api.list(video_id)

    transcript = ""
    for t in transcripts:
        if t.language_code == "en":
            if t.is_generated:
                if len(transcript) == 0:
                    transcript = t.fetch()
            else:
                transcript = t.fetch()
                break

    return transcript if transcript else None
```

Example snippet shape:

```json
[
  {"text": "We're no strangers to love.", "start": 0.0, "duration": 3.5},
  {"text": "You know the rules and so do I.", "start": 3.5, "duration": 4.0}
]
```

---

## 5. Process transcript to text

```python
def process(transcript):
    txt = ""
    for i in transcript:
        try:
            txt += f"Text: {i.text} Start: {i.start}\n"
        except KeyError:
            pass
    return txt
```

Example output:

```text
Text: We're no strangers to love. Start: 0.0
Text: You know the rules and so do I. Start: 3.5
Text: A full commitment's what I'm thinking of. Start: 7.5
```

---

## 6. Chunk transcript

```python
def chunk_transcript(processed_transcript, chunk_size=200, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_text(processed_transcript)
    return chunks
```

---

## 7. Watsonx setup (LLM + embeddings)

```python
def setup_credentials():
    model_id = "ibm/granite-8b-code-instruct"
    credentials = Credentials(url="https://us-south.ml.cloud.ibm.com")
    client = APIClient(credentials)
    project_id = "skills-network"
    return model_id, credentials, client, project_id


def define_parameters():
    return {
        GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
        GenParams.MAX_NEW_TOKENS: 900,
    }


def initialize_watsonx_llm(model_id, credentials, project_id, parameters):
    return WatsonxLLM(
        model_id=model_id,
        url=credentials.get("url"),
        project_id=project_id,
        params=parameters,
    )


def setup_embedding_model(credentials, project_id):
    return WatsonxEmbeddings(
        model_id="ibm/slate-30m-english-rtrvr-v2",
        url=credentials["url"],
        project_id=project_id,
    )
```

---

## 8. FAISS index + similarity search

```python
def create_faiss_index(chunks, embedding_model):
    return FAISS.from_texts(chunks, embedding_model)


def perform_similarity_search(faiss_index, query, k=3):
    return faiss_index.similarity_search(query, k=k)


def retrieve(query, faiss_index, k=7):
    return faiss_index.similarity_search(query, k=k)
```

---

## 9. Summary prompt + chain

```python
def create_summary_prompt():
    template = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an AI assistant tasked with summarizing YouTube video transcripts. Provide concise, informative summaries that capture the main points of the video content.

    Instructions:
    1. Summarize the transcript in a single concise paragraph.
    2. Ignore any timestamps in your summary.
    3. Focus on the spoken content (Text) of the video.

    Note: In the transcript, "Text" refers to the spoken words in the video, and "start" indicates the timestamp when that part begins in the video.<|eot_id|><|start_header_id|>user<|end_header_id|>
    Please summarize the following YouTube video transcript:

    {transcript}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    return PromptTemplate(input_variables=["transcript"], template=template)


def create_summary_chain(llm, prompt, verbose=True):
    return LLMChain(llm=llm, prompt=prompt, verbose=verbose)
```

---

## 10. QA prompt + chain + answer

```python
def create_qa_prompt_template():
    qa_template = """
    You are an expert assistant providing detailed answers based on the following video content.

    Relevant Video Context: {context}

    Based on the above context, please answer the following question:
    Question: {question}
    """
    return PromptTemplate(
        input_variables=["context", "question"],
        template=qa_template,
    )


def create_qa_chain(llm, prompt_template, verbose=True):
    return LLMChain(llm=llm, prompt=prompt_template, verbose=verbose)


def generate_answer(question, faiss_index, qa_chain, k=7):
    relevant_context = retrieve(question, faiss_index, k=k)
    answer = qa_chain.predict(context=relevant_context, question=question)
    return answer
```

---

## 11. Gradio actions (summarize / ask)

```python
processed_transcript = ""


def summarize_video(video_url):
    global fetched_transcript, processed_transcript

    if video_url:
        fetched_transcript = get_transcript(video_url)
        processed_transcript = process(fetched_transcript)
    else:
        return "Please provide a valid YouTube URL."

    if processed_transcript:
        model_id, credentials, client, project_id = setup_credentials()
        llm = initialize_watsonx_llm(
            model_id, credentials, project_id, define_parameters()
        )
        summary_prompt = create_summary_prompt()
        summary_chain = create_summary_chain(llm, summary_prompt)
        summary = summary_chain.run({"transcript": processed_transcript})
        return summary
    return "No transcript available. Please fetch the transcript first."


def answer_question(video_url, user_question):
    global fetched_transcript, processed_transcript

    if not processed_transcript:
        if video_url:
            fetched_transcript = get_transcript(video_url)
            processed_transcript = process(fetched_transcript)
        else:
            return "Please provide a valid YouTube URL."

    if processed_transcript and user_question:
        chunks = chunk_transcript(processed_transcript)
        model_id, credentials, client, project_id = setup_credentials()
        llm = initialize_watsonx_llm(
            model_id, credentials, project_id, define_parameters()
        )
        embedding_model = setup_embedding_model(credentials, project_id)
        faiss_index = create_faiss_index(chunks, embedding_model)
        qa_prompt = create_qa_prompt_template()
        qa_chain = create_qa_chain(llm, qa_prompt)
        return generate_answer(user_question, faiss_index, qa_chain)

    return "Please provide a valid question and ensure the transcript has been fetched."
```

---

## 12. Gradio UI

```python
with gr.Blocks() as interface:
    video_url = gr.Textbox(
        label="YouTube Video URL",
        placeholder="Enter the YouTube Video URL",
    )
    summary_output = gr.Textbox(label="Video Summary", lines=5)
    question_input = gr.Textbox(
        label="Ask a Question About the Video",
        placeholder="Ask your question",
    )
    answer_output = gr.Textbox(label="Answer to Your Question", lines=5)
    summarize_btn = gr.Button("Summarize Video")
    question_btn = gr.Button("Ask a Question")
    transcript_status = gr.Textbox(label="Transcript Status", interactive=False)

    summarize_btn.click(summarize_video, inputs=video_url, outputs=summary_output)
    question_btn.click(
        answer_question,
        inputs=[video_url, question_input],
        outputs=answer_output,
    )

interface.launch(server_name="0.0.0.0", server_port=7860)
```
