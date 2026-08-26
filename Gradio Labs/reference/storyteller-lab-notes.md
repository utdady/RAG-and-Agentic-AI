# Original lab notes (storyteller reference)

Source: IBM Skills Network-style notebook  
("Use Mistral and gTTS to Create Your Personal Storyteller").

**Not the runnable demo** — Watsonx / IPython Audio preserved for comparison.  
Runnable: `06_storyteller.py` (Groq/Ollama + gTTS + Gradio).

---

```python
%pip install gTTS==2.5.4
%pip install ibm-watsonx-ai==1.1.20

from ibm_watsonx_ai import Credentials, APIClient
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

credentials = Credentials(url="https://us-south.ml.cloud.ibm.com")
project_id = "skills-network"
client = APIClient(credentials)
model_id = "mistralai/mistral-medium-2505"

params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 1000,
}

model = ModelInference(
    model_id=model_id,
    credentials=credentials,
    project_id=project_id,
    params=params,
)

def generate_story(topic):
    prompt = f"""Write an engaging and educational story about {topic} for beginners.
            Use simple and clear language to explain basic concepts.
            Include interesting facts and keep it friendly and encouraging.
            The story should be around 200-300 words and end with a brief summary of what we learned.
            Make it perfect for someone just starting to learn about this topic."""
    return model.generate_text(prompt=prompt)

topic = "the life cycle of butterflies"
story = generate_story(topic)
print("Generated Story:\n", story)

from gtts import gTTS
from IPython.display import Audio
import io

tts = gTTS(story)
audio_bytes = io.BytesIO()
tts.write_to_fp(audio_bytes)
audio_bytes.seek(0)
Audio(audio_bytes.read(), autoplay=False)
tts.save("generated_story.mp3")

topic = "life cycle of a human"
story = generate_story(topic)
tts = gTTS(story)
# ... Audio(autoplay=True)
```

## Pivot

| Course | Here |
|--------|------|
| Watsonx Mistral | `shared.llm` |
| IPython `Audio` | Gradio `Audio` |
| Save `generated_story.mp3` in cwd | temp file for playback |
