# Original lab notes (reference)

Source: IBM Skills Network-style notebook  
("Build a Meeting Assistant with Whisper, LangChain, & Gradio").

**Not the runnable app** — this mirrors the course steps (Watsonx).  
Working app: [`../app.py`](../app.py) (Groq + Ollama via `shared.llm`).

Code blocks below are cleaned for readability (merged cell text from the paste was restored to normal newlines). Logic matches the original lab.

---

## 1. Install dependencies

```bash
pip install transformers==4.35.2 \
  torch==2.1.1 \
  gradio==5.9.0 \
  langchain==0.3.12 \
  langchain-community==0.3.12 \
  langchain_ibm==0.3.5 \
  ibm-watsonx-ai==1.1.16 \
  pydantic==2.10.3
```

```bash
sudo apt update
sudo apt install ffmpeg -y
```

---

## 2. Download sample meeting audio

```python
import requests

url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/hTqGqoC-LrW6S79HjuJUkg/trimmed-02.wav"
audio_file_path = "sample-meeting.wav"

response = requests.get(url)

if response.status_code == 200:
    with open(audio_file_path, "wb") as file:
        file.write(response.content)
    print("File downloaded successfully")
else:
    print("Failed to download the file")
```

---

## 3. Transcribe with Whisper (CLI smoke test)

```python
import torch
from transformers import pipeline

pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en",
    chunk_length_s=30,
)

sample = "sample-meeting.wav"
prediction = pipe(sample, batch_size=8)["text"]
print(prediction)
```

---

## 4. Gradio hello world

```python
import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch(server_name="0.0.0.0", server_port=5000)
```

---

## 5. Gradio audio transcription app

```python
import torch
from transformers import pipeline
import gradio as gr

def transcript_audio(audio_file):
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-tiny.en",
        chunk_length_s=30,
    )
    result = pipe(audio_file, batch_size=8)["text"]
    return result

audio_input = gr.Audio(sources="upload", type="filepath")
output_text = gr.Textbox()

iface = gr.Interface(
    fn=transcript_audio,
    inputs=audio_input,
    outputs=output_text,
    title="Audio Transcription App",
    description="Upload the audio file",
)

iface.launch(server_name="0.0.0.0", server_port=5000)
```

---

## 6. Watsonx Granite smoke test

```python
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from ibm_watsonx_ai.foundation_models.utils import get_embedding_model_specs
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

parameters = {
    GenParams.DECODING_METHOD: "sample",
    GenParams.MAX_NEW_TOKENS: 512,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.5,
    GenParams.TOP_K: 50,
    GenParams.TOP_P: 1,
}

model_id = "ibm/granite-4-h-small"
project_id = "skills-network"

granite_llm = WatsonxLLM(
    model_id=model_id,
    url="https://us-south.ml.cloud.ibm.com",
    project_id=project_id,
    params=parameters,
)

response = granite_llm.invoke("How to read a book effectively?")
print(response)
```

---

## 7. Financial product term helper (Llama on Watsonx)

Requires `credentials`, `project_id`, `TextChatParameters`, and `ModelInference` from the final app section (or Cloud IDE equivalents).

```python
def remove_non_ascii(text):
    return "".join(i for i in text if ord(i) < 128)


def product_assistant(ascii_transcript):
    system_prompt = """You are an intelligent assistant specializing in financial products;
    your task is to process transcripts of earnings calls, ensuring that all references to
    financial products and common financial terms are in the correct format. For each
    financial product or common term that is typically abbreviated as an acronym, the full term
    should be spelled out followed by the acronym in parentheses. For example, '401k' should be
    transformed to '401(k) retirement savings plan', 'HSA' should be transformed to
    'Health Savings Account (HSA)', 'ROA' should be transformed to 'Return on Assets (ROA)',
    'VaR' should be transformed to 'Value at Risk (VaR)', and 'PB' should be transformed to
    'Price to Book (PB) ratio'. Similarly, transform spoken numbers representing financial
    products into their numeric representations, followed by the full name of the product in
    parentheses. For instance, 'five two nine' to '529 (Education Savings Plan)' and
    'four zero one k' to '401(k) (Retirement Savings Plan)'. However, be aware that some
    acronyms can have different meanings based on the context (e.g., 'LTV' can stand for
    'Loan to Value' or 'Lifetime Value'). You will need to discern from the context which
    term is being referred to and apply the appropriate transformation. In cases where
    numerical figures or metrics are spelled out but do not represent specific financial
    products (like 'twenty three percent'), these should be left as is. Your role is to
    analyze and adjust financial product terminology in the text. Once you've done that,
    produce the adjusted transcript and a list of the words you've changed"""

    prompt_input = system_prompt + "\n" + ascii_transcript

    messages = [
        {
            "role": "user",
            "content": prompt_input,
        }
    ]

    model_id = "meta-llama/llama-3-2-11b-vision-instruct"

    params = TextChatParameters(
        temperature=0.2,
        top_p=0.6,
    )

    llama32 = ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id,
        params=params,
    )

    response = llama32.chat(messages=messages)
    return response["choices"][0]["message"]["content"]
```

---

## 8. Meeting minutes prompt + LangChain chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

template = """
Generate meeting minutes and a list of tasks based on the provided context.

Context:
{context}

Meeting Minutes:
- Key points discussed
- Decisions made

Task List:
- Actionable items with assignees and deadlines
"""

prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

---

## 9. Final app (Watsonx + Whisper + Gradio)

Single consolidated notebook-style script from the end of the lab.

```python
import torch
import os
import gradio as gr
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from ibm_watsonx_ai.foundation_models import ModelInference
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from transformers import pipeline

# ------- LLM Initialization -------
project_id = "skills-network"
credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    # api_key="<YOUR_API_KEY>"  # Cloud IDE often injects this
)
client = APIClient(credentials)
model_id = "ibm/granite-4-h-small"

parameters = {
    GenParams.DECODING_METHOD: "sample",
    GenParams.MAX_NEW_TOKENS: 512,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.5,
    GenParams.TOP_K: 50,
    GenParams.TOP_P: 1,
}

llm = WatsonxLLM(
    model_id=model_id,
    url="https://us-south.ml.cloud.ibm.com",
    project_id=project_id,
    params=parameters,
)

# ------- Helper Functions -------
def remove_non_ascii(text):
    return "".join(i for i in text if ord(i) < 128)


def product_assistant(ascii_transcript):
    system_prompt = """You are an intelligent assistant specializing in financial products;
    your task is to process transcripts of earnings calls, ensuring that all references to
    financial products and common financial terms are in the correct format. For each
    financial product or common term that is typically abbreviated as an acronym, the full term
    should be spelled out followed by the acronym in parentheses. For example, '401k' should be
    transformed to '401(k) retirement savings plan', 'HSA' should be transformed to
    'Health Savings Account (HSA)', 'ROA' should be transformed to 'Return on Assets (ROA)',
    'VaR' should be transformed to 'Value at Risk (VaR)', and 'PB' should be transformed to
    'Price to Book (PB) ratio'. Similarly, transform spoken numbers representing financial
    products into their numeric representations, followed by the full name of the product in
    parentheses. For instance, 'five two nine' to '529 (Education Savings Plan)' and
    'four zero one k' to '401(k) (Retirement Savings Plan)'. However, be aware that some
    acronyms can have different meanings based on the context (e.g., 'LTV' can stand for
    'Loan to Value' or 'Lifetime Value'). You will need to discern from the context which
    term is being referred to and apply the appropriate transformation. In cases where
    numerical figures or metrics are spelled out but do not represent specific financial
    products (like 'twenty three percent'), these should be left as is. Your role is to
    analyze and adjust financial product terminology in the text. Once you've done that,
    produce the adjusted transcript and a list of the words you've changed"""

    prompt_input = system_prompt + "\n" + ascii_transcript
    messages = [
        {
            "role": "user",
            "content": prompt_input,
        }
    ]

    adjusted_model_id = "meta-llama/llama-3-2-11b-vision-instruct"
    params = TextChatParameters(
        temperature=0.2,
        top_p=0.6,
    )
    llama32 = ModelInference(
        model_id=adjusted_model_id,
        credentials=credentials,
        project_id=project_id,
        params=params,
    )
    response = llama32.chat(messages=messages)
    return response["choices"][0]["message"]["content"]


# ------- Prompt Template and Chain -------
template = """
Generate meeting minutes and a list of tasks based on the provided context.

Context:
{context}

Meeting Minutes:
- Key points discussed
- Decisions made

Task List:
- Actionable items with assignees and deadlines
"""

prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# ------- Speech2text and Pipeline -------
def transcript_audio(audio_file):
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-medium",
        chunk_length_s=30,
    )
    raw_transcript = pipe(audio_file, batch_size=8)["text"]
    ascii_transcript = remove_non_ascii(raw_transcript)
    adjusted_transcript = product_assistant(ascii_transcript)
    result = chain.invoke({"context": adjusted_transcript})

    output_file = "meeting_minutes_and_tasks.txt"
    with open(output_file, "w") as file:
        file.write(result)

    return result, output_file


# ------- Gradio Interface -------
audio_input = gr.Audio(
    sources="upload",
    type="filepath",
    label="Upload your audio file",
)
output_text = gr.Textbox(label="Meeting Minutes and Tasks")
download_file = gr.File(label="Download the Generated Meeting Minutes and Tasks")

iface = gr.Interface(
    fn=transcript_audio,
    inputs=audio_input,
    outputs=[output_text, download_file],
    title="AI Meeting Assistant",
    description=(
        "Upload an audio file of a meeting. This tool will transcribe the audio, "
        "fix product-related terminology, and generate meeting minutes along with "
        "a list of tasks."
    ),
)

iface.launch(server_name="0.0.0.0", server_port=5000)
```
