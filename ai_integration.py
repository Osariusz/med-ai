import requests
from dataclasses import dataclass
from typing import Any
from redis_integration import k_nearest_neighbors

class AiService:
    def __init__(self, ai_url: str, ai_model: str):
        self.ai_url = ai_url
        self.ai_model = ai_model

    def generate_medical_advice(self, user_input: str) -> str:

        paragraphs: list[str] = k_nearest_neighbors(user_input)

        prompt = (
            f"""# Kontekst:
Jesteś znanym i renomowanym lekarzem specjalistą. Twoim głównym zadaniem jest stawianie diagnozy i proponowanie leczenia na podstawie tego, co mówi pacjent. Skup się przede wszystkim na objawach i opisie problemu przekazanym przez pacjenta. Zwróć uwagę na miejsce pobytu pacjenta, potencjalne narażenie na określone choroby opisane w źródłach oraz inne istotne czynniki. Otrzymasz także kilka źródeł (np. artykułów naukowych), które mogą stanowić wsparcie, ale traktuj je jako drugorzędne względem relacji pacjenta. Oceń, na co może cierpieć pacjent, i zaproponuj odpowiednie kroki leczenia.

# Źródła:
{paragraphs}
# Wiadomość pacjenta:
{user_input}
# Odpowiedź lekarza:
"""
        )
        
        generation_payload = {
            "model": self.ai_model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.ai_url}/api/generate",
                json=generation_payload,
                timeout=10
            )

            response.raise_for_status()

            result = response.json()
            if 'response' not in result:
                raise ValueError("Invalid response format from AI API")

            return result['response']

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error communicating with AI API: {e}") from e
        except ValueError as e:
            raise ValueError(f"Error processing AI response: {e}") from e