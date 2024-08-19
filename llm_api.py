from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deep_translator import GoogleTranslator
import ollama

app = FastAPI()
translator = GoogleTranslator(source='ar', target='en')

class StoryInput(BaseModel):
    name: str
    age: int
    dream: str
    country: str

def translate_to_english(text: str) -> str:
    return translator.translate(text)

def translate_to_arabic(text: str) -> str:
    translator = GoogleTranslator(source='en', target='ar')
    return translator.translate(text)

def get_bot_response(name: str, age: int, dream: str, country: str) -> str:
    prompt_template = (
    f"Create a story for {name}, who is {age} years old. {name} has a dream of becoming a {dream} in {country}. "
    "Focus on their growth, challenges, and eventual success."
    )


    # Interact with Ollama here
    response = ollama.chat(model="llama3.1", messages=[{'role': 'user', 'content': prompt_template}])
    return response['message']['content']

@app.post("/generate_story/")
def generate_story(story_input: StoryInput):
    # Translate input fields to English
    name_en = translate_to_english(story_input.name)
    age_en = story_input.age  # Age doesn't need translation
    dream_en = translate_to_english(story_input.dream)
    country_en = translate_to_english(story_input.country)

    story = get_bot_response(name_en, age_en, dream_en, country_en)
    sentences = story.split('. ')
    
    # Ensure the story has exactly 5 sentences
    if len(sentences) < 5:
        sentences += [""] * (5 - len(sentences))
    else:
        sentences = sentences[:5]

    # Translate the sentences to Arabic
    sentences_arabic = [translate_to_arabic(sentence) for sentence in sentences]

    return {"sentences_en": sentences, "sentences_ar": sentences_arabic}
