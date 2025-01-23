#### Opis projektu
System AI umożliwia pacjentowi opisanie swoich symptomów, a następnie:
1. Wyszukuje odpowiednie artykuły medyczne w bazie danych Redis.
2. Streszcza znalezione artykuły i przekazuje je do prompta generującego odpowiedź.
3. Tworzy spersonalizowaną odpowiedź na podstawie symptomów pacjenta i streszczeń.

#### Architektura systemu
1. **Silnik wyszukiwania**: Analizuje symptomy i formułuje zapytania do bazy Redis.
2. **Baza danych Redis**: Przechowuje artykuły medyczne, umożliwiając szybkie wyszukiwanie.
3. **Moduł streszczania**: Generuje krótkie podsumowania artykułów.
4. **Moduł generowania odpowiedzi**: Tworzy odpowiedź dla pacjenta na podstawie symptomów i streszczeń.

#### Przebieg działania
1. Pacjent opisuje swoje symptomy.
2. AI analizuje symptomy i wyszukuje artykuły w Redis.
3. Streszczone artykuły trafiają do prompta generującego odpowiedź.
4. AI formułuje odpowiedź dla pacjenta.

#### Przykłady promptów
- **Prompt do streszczania artykułów**:
```# Kontekst:
Jesteś znanym i renomowanym lekarzem specjalistą. Dostaniesz artykuł naukowy o schorzeniu ze szczegółami jego leczenia, dawkami lekarstw i tak dalej. Twoim zadaniem jest streścić ten artykuł do nazwy zwyczajowej, objawów i sposobów leczenia zgodnie ze schematem. Twoja wypowiedź nie może przekroczyć 400 znaków.
# Schemat:
Nazwa:
Objawy:
Leczenie:
# Artykuł naukowy:
{article}
# Streszczenie artykułu:
```
- **Prompt do generowania odpowiedzi**: 
```# Kontekst:
Jesteś renomowanym lekarzem, diagnozujesz i leczysz na podstawie objawów podanych przez pacjenta. Skup się na ich opisie, uwzględnij miejsce pobytu i czynniki ryzyka. Źródła traktuj jako pomocnicze. Podaj możliwe choroby i proponowane leczenie, używając prostego, zrozumiałego języka.
# Źródła dla lekarza:
{paragraphs_for_prompt}
# Dolegliwości pacjenta:
{user_input}
# Odpowiedź lekarza:
```

#### Tech Stack
- **Języki**: Python
- **Bazy danych**: Redis
- **Modele LLM**: Bielik 7B
