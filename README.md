# Zadanie domowe #11
Celem tego zadania domowego jest stworzenie interfejsu REST API do przechowywania i zarządzania kontaktami. API powinno być zbudowane przy użyciu infrastruktury FastAPI i używać SQLAlchemy do zarządzania bazą danych.

Kontakty powinny być przechowywane w bazie danych i zawierać następujące informacje:

1. Imię
2. Nazwisko
3. Adres e-mail
4. Numer telefonu
5. Datę urodzenia
6. Dodatkowe dane (opcjonalnie)

Interfejs API powinien być w stanie wykonywać następujące czynności:

1. Utworzyć nowy kontakt
2. Pobrać listę wszystkich kontaktów
3. Pobrać jeden kontakt według ID
4. Zaktualizować istniejący kontakt
5. Usunąć kontakt

Oprócz podstawowej funkcjonalności, CRUD API powinien mieć również następujące cechy:

1. Kontakty powinny być przeszukiwalne według imienia, nazwiska lub adresu e-mail (Query).
2. API powinno być w stanie pobrać listę kontaktów z datami urodzin na najbliższe 7 dni.

## Wymagania ogólne
1. Użycie frameworka FastAPI do tworzenia API.
2. Użycie SQLAlchemy ORM do pracy z bazą danych.
3. Jako bazy danych należy użyć PostgreSQL.
4. Obsługa operacji CRUD dla kontaktów.
5. Obsługa przechowywania daty urodzenia kontaktu.
6. Dostarczenie dokumentów dla API.
7. Użycie modułu walidacji danych Pydantic.