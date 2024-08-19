from auth_token import auth_token
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from io import BytesIO
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_credentials=True, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = "CompVis/stable-diffusion-v1-4"
pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=auth_token)
pipe.to(device)

class GenerateImagesRequest(BaseModel):
    prompts: list[str]


@app.post("/generate_images/")
def generate_images(request: GenerateImagesRequest):
    images = []
    for prompt in request.prompts:
        
        animation_prompt = f"Create an animation-style or cartoon illustration based on the following: {prompt}"

        with autocast(device) if device != "mps" else torch.no_grad():
            image = pipe(animation_prompt, guidance_scale=8.5).images[0]

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        imgstr = base64.b64encode(buffer.getvalue()).decode("utf-8")
        images.append(imgstr)

    return {"images": images}

