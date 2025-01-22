from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from ai_integration import AiService
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
ai_service = AiService(ai_url=os.getenv("AI_URL"), ai_model=os.getenv("AI_MODEL"))

origins = [
    "http://localhost:5173",  # Allow requests from React/Next.js dev servers
    os.getenv(f"FRONT_URL")
]

# Add the CORSMiddleware to your FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify allowed origins
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all HTTP headers
)

@app.get("/medical-advice")
def get_medical_advice(symptoms: str):
    print("starting medical advice")
    advice = ai_service.generate_medical_advice(symptoms)
    advice = advice.replace("\n", "<br/>")
    return advice

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
