# Gra Inwestycyjna (Streamlit)

Edukacyjna gra inwestycyjna napisana w **Streamlit**, w której podejmujesz decyzje inwestycyjne w kolejnych rundach i obserwujesz wpływ swoich wyborów na kapitał oraz profil inwestora.

👉 **Gra online:** https://investmentgame.streamlit.app/

---

## Na czym polega gra?

- Gra składa się z **40 rund**, z których każda odpowiada jednemu miesiącowi.
- Startujesz z kapitałem **10 000 PLN**.
- W każdej rundzie wybierasz **jeden instrument**, w który inwestujesz na kolejny miesiąc.

Dostępne instrumenty:
- **S&P 500** – niższe / średnie ryzyko
- **Złoto** – średnie ryzyko
- **Bitcoin** – wysokie ryzyko
- **Gotówka** – brak ryzyka (0% zwrotu)

Od **20. rundy** możesz dodatkowo użyć **dźwigni finansowej (lewar x2)**, która podwaja zarówno zyski, jak i straty.

---

## Jak działa symulacja?

- Zwroty są **losowe**, ale:
  - mają realistyczną zmienność,
  - uwzględniają rzadkie skoki (crash / rally),
  - posiadają lekką „pamięć trendu” (momentum),
  - są ograniczone widełkami, aby uniknąć absurdalnych wyników.
- Każdy instrument ma **własne parametry ryzyka**.

---

## Co widzisz w trakcie gry?

- Aktualny kapitał i miesięczną zmianę procentową.
- Wykres porównujący:
  - Twój kapitał
  - S&P 500
  - Złoto
  - Bitcoin
- Informację o dostępności lewara.

---

## Podsumowanie po zakończeniu gry

Po 40 rundach otrzymujesz pełne podsumowanie:

### 1. Wyniki finansowe
- Końcowy kapitał gracza.
- Wyniki benchmarków (S&P 500, Złoto, Bitcoin).
- Czytelne kafelki z wartościami (bez ucinania liczb).

### 2. Historia decyzji
- Tabela wszystkich rund:
  - instrument,
  - użycie lewara,
  - zwrot procentowy,
  - kapitał po rundzie.

### 3. Ocena inwestora

Gra oblicza dwa wskaźniki (0–100):

#### Skłonność do ryzyka
Rośnie, jeśli:
- często wybierasz **Bitcoin**,
- używasz **lewara**,
- silnie koncentrujesz się na jednym aktywie.

Spada, jeśli:
- często trzymasz **gotówkę**,
- dominującym wyborem jest **S&P 500**.

#### Racjonalność
Spada, jeśli:
- trzymasz instrument mimo **serii spadków**,
- używasz **lewara po spadkach**,
- często zmieniasz instrument (overtrading),
- kupujesz po silnych wzrostach („euforia”).

Może rosnąć, jeśli:
- unikasz lewara w trudnych momentach,
- przechodzisz do gotówki lub bezpieczniejszych aktywów po spadkach,
- ograniczasz impulsywne decyzje.

Na końcu wyświetlane jest także **wyjaśnienie oceny** oraz statystyki Twoich wyborów.

---

## Jak uruchomić lokalnie?

### Wymagania
- Python 3.9+
- Biblioteki: `streamlit`, `pandas`

### Instalacja
```bash
pip install streamlit pandas
```

### Uruchomienie
```bash
streamlit run app.py
```

---

## Cel gry

Gra nie ma przewidywać rynku. Jej celem jest:
- pokazanie wpływu **ryzyka**, **koncentracji** i **lewara**,
- nauka konsekwencji decyzji inwestycyjnych,
- refleksja nad własnym stylem inwestowania.


