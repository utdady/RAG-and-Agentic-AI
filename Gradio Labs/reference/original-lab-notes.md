# Original lab notes (reference)

Source: IBM Skills Network-style notebook  
("Set Up a Simple Gradio Interface to Interact with Your Models").

**Not the runnable demos** — Watsonx cells preserved for comparison.  
Runnable scripts: `01_*.py` … `03_*.py` (Groq/Ollama for chat).

---

```python
# Gradio: add numbers
import gradio as gr
from huggingface_hub import HfFolder  # unused in original

def add_numbers(Num1, Num2):
    return Num1 + Num2

demo = gr.Interface(
    fn=add_numbers,
    inputs=[gr.Number(), gr.Number()],
    outputs=gr.Number()
)
demo.launch(server_name="127.0.0.1", server_port=7860)

# Gradio: sentence builder (widgets)
def sentence_builder(quantity, tech_worker_type, countries, place, activity_list, morning):
    return f"""The {quantity} {tech_worker_type}s from {" and ".join(countries)} went to the {place} where they {" and ".join(activity_list)} until the {"morning" if morning else "night"}"""

demo = gr.Interface(
    fn=sentence_builder,
    inputs=[
        gr.Slider(3, 20, value=4, step=1, label="Count", info="Choose between 3 and 20"),
        gr.Dropdown(
            ["Data Scientist", "Software Developer", "Software Engineer"],
            label="tech_worker_type",
            info="Will add more tech worker types later!"
        ),
        gr.CheckboxGroup(["Canada", "Japan", "France"], label="Countries", info="Where are they from?"),
        gr.Radio(["office", "restaurant", "meeting room"], label="Location", info="Where did they go?"),
        gr.Dropdown(
            ["partied", "brainstormed", "coded", "fixed bugs"],
            value=["brainstormed", "fixed bugs"],
            multiselect=True,
            label="Activities",
            info="Which activities did they perform?"
        ),
        gr.Checkbox(label="Morning", info="Did they do it in the morning?"),
    ],
    outputs="text",
    examples=[
        [3, "Software Developer", ["Canada", "Japan"], "restaurant", ["coded", "fixed bugs"], True],
        [4, "Data Scientist", ["Japan"], "office", ["brainstormed", "partied"], False],
        [10, "Software Engineer", ["Canada", "France"], "meeting room", ["brainstormed"], False],
        [8, "Data Scientist", ["France"], "restaurant", ["coded"], True],
    ]
)
demo.launch(server_name="127.0.0.1", server_port=7860)

# WatsonxLLM CLI
from langchain_ibm import WatsonxLLM
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

model_id = 'meta-llama/llama-3-2-11b-vision-instruct'
parameters = {
    GenParams.MAX_NEW_TOKENS: 256,
    GenParams.TEMPERATURE: 0.5,
}
watsonx_llm = WatsonxLLM(
    model_id=model_id,
    url="https://us-south.ml.cloud.ibm.com",
    project_id="skills-network",
    params=parameters,
)
query = input("Please enter your query: ")
print(watsonx_llm.invoke(query))

# Gradio + WatsonxLLM chat
def generate_response(prompt_txt):
    return watsonx_llm.invoke(prompt_txt)

chat_application = gr.Interface(
    fn=generate_response,
    allow_flagging="never",
    inputs=gr.Textbox(label="Input", lines=2, placeholder="Type your question here..."),
    outputs=gr.Textbox(label="Output"),
    title="Watsonx.ai Chatbot",
    description="Ask any question and the chatbot will try to answer."
)
chat_application.launch(server_name="127.0.0.1", server_port=7860)
# Optional tweak in lab: GenParams.MAX_NEW_TOKENS: 512
```
