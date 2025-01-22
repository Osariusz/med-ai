import requests
from dataclasses import dataclass
from typing import Any
from redis_integration import k_nearest_neighbors

class AiService:
    def __init__(self, ai_url: str, ai_model: str):
        self.ai_url = ai_url
        self.ai_model = ai_model

    def summarize_article(self, article: str) -> str:
        MAX_ARTICLE_LENGTH = 20
        if(len(article) > MAX_ARTICLE_LENGTH):
            article = article[:MAX_ARTICLE_LENGTH]
        prompt = (
            f"""# Kontekst:
Jesteś znanym i renomowanym lekarzem specjalistą. Dostaniesz artykuł naukowy o schorzeniu ze szczegółami jego leczenia, dawkami lekarstw i tak dalej. Twoim zadaniem jest streścić ten artykuł do nazwy zwyczajowej, objawów i sposobów leczenia zgodnie ze schematem. Twoja wypowiedź nie może przekroczyć 500 znaków.
# Schemat:
Nazwa:
Objawy:
Leczenie:
# Artykuł naukowy:
{article}
# Streszczenie artykułu:
"""
        )
        print(prompt)
        print(len(prompt))
        generation_payload = {
            "model": self.ai_model,
            "prompt": prompt,
            "stream": False
        }

        exception_occured = True        
        while(exception_occured):
            print("try generating")
            try:
                response = requests.post(
                    f"{self.ai_url}/api/generate",
                    json=generation_payload,
                    timeout=300
                )

                response.raise_for_status()

                result = response.json()
                if 'response' not in result:
                    raise ValueError("Invalid response format from AI API")
                exception_occured = False
                return result['response']

            except Exception as e:
                exception_occured = True


    def generate_medical_advice(self, user_input: str) -> str:
        print("asking ai")
        paragraphs: list[str] = k_nearest_neighbors(user_input)

        def modify_article(article: str):
            summarized_article: str = self.summarize_article(article)
            MAX_SUMMARY_LENGTH = 100
            if(len(summarized_article) > MAX_SUMMARY_LENGTH):
                return summarized_article[:MAX_SUMMARY_LENGTH]
            return summarized_article

        paragraphs = [modify_article(paragraph) for paragraph in paragraphs]
        paragraphs_for_prompt = "\n".join(paragraphs)
        MAX_ARTICLES_PART_LENGTH = 700
        if(len(paragraphs_for_prompt) > MAX_ARTICLES_PART_LENGTH):
            paragraphs_for_prompt = paragraphs_for_prompt[:MAX_ARTICLES_PART_LENGTH]

        prompt = (
            f"""# Kontekst:
Jesteś znanym i renomowanym lekarzem specjalistą. Twoim głównym zadaniem jest stawianie diagnozy i proponowanie leczenia na podstawie tego, co mówi pacjent. Skup się przede wszystkim na objawach i opisie problemu przekazanym przez pacjenta. Zwróć uwagę na miejsce pobytu pacjenta, potencjalne narażenie na określone choroby opisane w źródłach oraz inne istotne czynniki. Otrzymasz także kilka źródeł (np. artykułów naukowych), które mogą stanowić wsparcie, ale traktuj je jako drugorzędne względem relacji pacjenta. Oceń, na co może cierpieć pacjent, i zaproponuj odpowiednie kroki leczenia. Mów krótko, wymień możliwe choroby i mów językiem zrozumiałym dla pacjenta.

# Źródła dla lekarza:
{paragraphs_for_prompt}
# Dolegliwości pacjenta:
{user_input}
# Odpowiedź lekarza:
"""
        )
        print(prompt)
        MAX_PROMPT = 100
        if(len(prompt) > MAX_PROMPT):
             print("warning too many char in prompt")
             prompt = prompt[len(prompt)-MAX_PROMPT:]
        generation_payload = {
            "model": self.ai_model,
            "prompt": prompt,
            "stream": False
        }


        exception_occured = True        
        while(exception_occured):
            print("try generating")
            try:
                response = requests.post(
                    f"{self.ai_url}/api/generate",
                    json=generation_payload,
                    timeout=300
                )

                response.raise_for_status()

                result = response.json()
                if 'response' not in result:
                    raise ValueError("Invalid response format from AI API")
                exception_occured = False
                return result['response']

            except Exception as e:
                exception_occured = True
