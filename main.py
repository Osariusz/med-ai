from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from ai_integration import AiService

app = FastAPI()
ai_service = AiService(ai_url=os.getenv("AI_URL"), ai_model=os.getenv("AI_MODEL"))

@app.get("/medical-advice")
def get_medical_advice(symptoms: str):
    print("starting medical advice")
    advice = ai_service.generate_medical_advice(symptoms)
    return advice

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
