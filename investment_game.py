import streamlit as st
import pandas as pd
import random
import textwrap  # Renderowanie HTML

# Ustawienia strony aplikacji
st.set_page_config(page_title="Gra Inwestycyjna", layout="centered")

# Style CSS dla całej aplikacji
st.markdown("""
<style>
.stButton>button { height: 3em; font-weight: bold; }
.instruction-card {
    background-color: #f8f9fa;
    border-left: 6px solid #003366;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    margin-bottom: 25px;
    color: #2c3e50;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.instruction-card h3 {
    margin-top: 0;
    color: #003366;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 1rem;
    letter-spacing: 1px;
}
.instruction-card ul { padding-left: 20px; line-height: 1.6; }
.instruction-card li { margin-bottom: 10px; }
.important-text {
    color: #003366;
    font-weight: 800;
    font-size: 1.05em;
    text-decoration: underline;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Style kafelków podsumowania */
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 8px; }
.summary-card {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px;
    padding: 18px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    min-width: 0;
}

/* Wymuszamy pełne wyświetlanie tekstu bez "..." */
.summary-card, .summary-card * {
    overflow: visible !important;
    text-overflow: clip !important;
}

.summary-title { font-size: 1.25rem; font-weight: 800; color: #111827; margin-bottom: 10px; }
.summary-value {
    font-size: 1.25rem;
    font-weight: 900;
    color: #111827;
    line-height: 1.25;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    margin-bottom: 14px;
}
.summary-ccy { font-size: 0.95em; font-weight: 800; color: #374151; }
.summary-delta { margin-top: 0; font-size: 1.25rem; font-weight: 900; }
.delta-pos { color: #1b5e20; background: #e8f5e9; display: inline-block; padding: 10px 14px; border-radius: 999px; }
.delta-neg { color: #b71c1c; background: #ffebee; display: inline-block; padding: 10px 14px; border-radius: 999px; }

@media (max-width: 900px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# Liczba rund w grze
TOTAL_ROUNDS = 40

# Etykiety rund do wyświetlenia na ekranie
LABELS_TEXT = [
    "wrz 22", "paź 22", "lis 22", "gru 22", "sty 23", "lut 23", "mar 23", "kwi 23", "maj 23", "cze 23",
    "lip 23", "sie 23", "wrz 23", "paź 23", "lis 23", "gru 23", "sty 24", "lut 24", "mar 24", "kwi 24",
    "maj 24", "cze 24", "lip 24", "sie 24", "wrz 24", "paź 24", "lis 24", "gru 24", "sty 25", "lut 25",
    "mar 25", "kwi 25", "maj 25", "cze 25", "lip 25", "sie 25", "wrz 25", "paź 25", "lis 25", "gru 25"
]

# Uzupełniamy listę historią do stałej długości, żeby wykresy miały stały rozmiar
def pad_history(history_list, total_length):
    base = history_list[:total_length]
    padding = [None] * (total_length - len(base))
    return base + padding

# Zmieniamy stronę w aplikacji i odświeżamy widok
def next_page(page_name: str):
    st.session_state.page = page_name
    st.rerun()

# Formatujemy liczbę jako PLN bez części dziesiętnej
def fmt_pln_num(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")

# Formatujemy wartość procentową z plusem dla dodatnich wyników
def fmt_pct(x: float) -> str:
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.2f}%"

# Parametry instrumentów do losowania zwrotów
INSTRUMENTS = {
    "SP500": {
        "label": "S&P 500",
        "mean": 0.006,
        "vol": 0.035,
        "crash_p": 0.015,
        "crash_mu": -0.08,
        "crash_sigma": 0.03,
        "rally_p": 0.012,
        "rally_mu": 0.07,
        "rally_sigma": 0.03,
        "mom_strength": 0.03,
        "mom_cap": 0.03,
        "ret_floor": -0.15,
        "ret_cap": 0.15,
    },
    "GOLD": {
        "label": "Złoto",
        "mean": 0.0035,
        "vol": 0.040,
        "crash_p": 0.012,
        "crash_mu": -0.07,
        "crash_sigma": 0.03,
        "rally_p": 0.012,
        "rally_mu": 0.07,
        "rally_sigma": 0.03,
        "mom_strength": 0.03,
        "mom_cap": 0.035,
        "ret_floor": -0.12,
        "ret_cap": 0.12,
    },
    "BTC": {
        "label": "Bitcoin",
        "mean": 0.010,
        "vol": 0.10,
        "crash_p": 0.040,
        "crash_mu": -0.22,
        "crash_sigma": 0.08,
        "rally_p": 0.035,
        "rally_mu": 0.20,
        "rally_sigma": 0.08,
        "mom_strength": 0.035,
        "mom_cap": 0.05,
        "ret_floor": -0.35,
        "ret_cap": 0.35,
    },
    "CASH": {
        "label": "Gotówka",
        "mean": 0.0,
        "vol": 0.0,
        "crash_p": 0.0,
        "crash_mu": 0.0,
        "crash_sigma": 0.0,
        "rally_p": 0.0,
        "rally_mu": 0.0,
        "rally_sigma": 0.0,
        "mom_strength": 0.0,
        "mom_cap": 0.0,
        "ret_floor": 0.0,
        "ret_cap": 0.0,
    }
}

# Wyliczamy lekką przewagę trendu na podstawie ostatnich zwrotów
def streak_bias(instr_key: str, lookback: int = 4) -> float:
    if instr_key == "CASH":
        return 0.0

    p = INSTRUMENTS[instr_key]
    key_map = {"SP500": "returns_sp", "GOLD": "returns_gold", "BTC": "returns_btc"}
    series = st.session_state.get(key_map[instr_key], [])
    if not series:
        return 0.0

    last = series[-lookback:]
    score = sum(1 if x > 0 else (-1 if x < 0 else 0) for x in last)
    raw = (score / lookback) * p["mom_strength"]
    return max(-p["mom_cap"], min(p["mom_cap"], raw))

# Ograniczamy wartość do podanego zakresu
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

# Losujemy zwrot instrumentu z uwzględnieniem skrajnych zdarzeń i trendu
def sample_return(instr_key: str) -> float:
    p = INSTRUMENTS[instr_key]
    if instr_key == "CASH":
        return 0.0

    bias = streak_bias(instr_key)
    u = random.random()

    if u < p["crash_p"]:
        r = random.gauss(p["crash_mu"], p["crash_sigma"])
    elif u < p["crash_p"] + p["rally_p"]:
        r = random.gauss(p["rally_mu"], p["rally_sigma"])
    else:
        r = random.gauss(p["mean"] + bias, p["vol"])

    return clamp(r, p["ret_floor"], p["ret_cap"])

# Inicjujemy stronę startową, jeśli jeszcze jej nie ma w stanie sesji
if "page" not in st.session_state:
    st.session_state.page = "game1_intro"

# Ustawiamy stan gry na wartości początkowe
def init_game_state():
    st.session_state.g1_round = 0
    st.session_state.g1_capital = 10000.0
    st.session_state.g1_history_user = [10000.0]

    st.session_state.hist_sp = [10000.0]
    st.session_state.hist_gold = [10000.0]
    st.session_state.hist_btc = [10000.0]

    st.session_state.returns_sp = []
    st.session_state.returns_gold = []
    st.session_state.returns_btc = []

    st.session_state.g1_decisions = []

# Zapewniamy, że zwroty na kolejne rundy są już wylosowane
def ensure_round_returns(next_round_index: int):
    while len(st.session_state.returns_sp) < next_round_index:
        st.session_state.returns_sp.append(sample_return("SP500"))
    while len(st.session_state.returns_gold) < next_round_index:
        st.session_state.returns_gold.append(sample_return("GOLD"))
    while len(st.session_state.returns_btc) < next_round_index:
        st.session_state.returns_btc.append(sample_return("BTC"))

# Aktualizujemy wyniki benchmarków na podstawie wylosowanych zwrotów
def apply_benchmarks(next_round_index: int):
    r_sp = st.session_state.returns_sp[next_round_index - 1]
    r_gold = st.session_state.returns_gold[next_round_index - 1]
    r_btc = st.session_state.returns_btc[next_round_index - 1]

    st.session_state.hist_sp.append(st.session_state.hist_sp[-1] * (1 + r_sp))
    st.session_state.hist_gold.append(st.session_state.hist_gold[-1] * (1 + r_gold))
    st.session_state.hist_btc.append(st.session_state.hist_btc[-1] * (1 + r_btc))

# Budujemy jedno zdanie podsumowania profilu inwestora
def investor_sentence(rationality: int, risk: int) -> str:
    if rationality < 35:
        r_txt = "mało racjonalnym"
    elif rationality < 65:
        r_txt = "umiarkowanie racjonalnym"
    else:
        r_txt = "racjonalnym"

    if risk < 35:
        k_txt = "niską"
        style = "defensywny"
    elif risk < 65:
        k_txt = "umiarkowaną"
        style = "zbalansowany"
    else:
        k_txt = "wysoką"
        style = "agresywny"

    return (
        f"Jesteś {r_txt} inwestorem z {k_txt} skłonnością do ryzyka. "
        f"Twoje decyzje sugerują styl: {style}."
    )

# Liczymy ocenę gracza na podstawie historii decyzji
def compute_player_scores():
    decisions = st.session_state.get("g1_decisions", [])
    if not decisions:
        return {"risk": 0, "rationality": 0, "notes": ["Brak decyzji do oceny."]}

    key_map = {"SP500": "returns_sp", "GOLD": "returns_gold", "BTC": "returns_btc"}

    n = len(decisions)
    counts = {"SP500": 0, "GOLD": 0, "BTC": 0, "CASH": 0}
    lev_count = 0
    switches = 0

    prev_choice = None
    for d in decisions:
        ch = d["choice"]
        counts[ch] += 1
        if d.get("leverage"):
            lev_count += 1
        if prev_choice is not None and ch != prev_choice:
            switches += 1
        prev_choice = ch

    share = {k: counts[k] / n for k in counts}
    share_lev = lev_count / n
    switch_rate = switches / max(1, (n - 1))

    concentration = sum(v**2 for v in share.values())

    risk_raw = (
        0.90 * share["BTC"] +
        0.25 * share["GOLD"] -
        0.35 * share["SP500"] +
        0.90 * share_lev +
        0.25 * concentration -
        0.85 * share["CASH"]
    )
    risk = int(max(0, min(100, round(50 + 70 * risk_raw))))

    penalties = 0.0
    bonuses = 0.0

    def neg_streak(series, upto_index_exclusive, window=3):
        start = max(0, upto_index_exclusive - window)
        ctx = series[start:upto_index_exclusive]
        s = 0
        for x in reversed(ctx):
            if x < 0:
                s += 1
            else:
                break
        return s

    def big_up(series, upto_index_exclusive, threshold=0.08):
        if upto_index_exclusive - 1 < 0 or upto_index_exclusive - 1 >= len(series):
            return False
        return series[upto_index_exclusive - 1] >= threshold

    for d in decisions:
        r = d["round"]
        ch = d["choice"]
        lev = d.get("leverage", False)

        if ch == "CASH":
            btc_series = st.session_state.get("returns_btc", [])
            btc_ns = neg_streak(btc_series, r - 1, window=3)
            if btc_ns >= 2:
                bonuses += 0.35
            continue

        series = st.session_state.get(key_map[ch], [])

        ns = neg_streak(series, r - 1, window=3)
        if ns >= 2:
            mult = 1.0
            if ch == "BTC":
                mult = 1.35
            elif ch == "GOLD":
                mult = 1.15
            penalties += mult * (ns - 1)

        if lev:
            last2_start = max(0, (r - 1) - 2)
            last2 = series[last2_start:(r - 1)]
            if len(last2) == 2 and all(x < 0 for x in last2):
                penalties += 1.2 if ch != "SP500" else 0.9

        if big_up(series, r - 1, threshold=0.10 if ch == "BTC" else 0.06):
            penalties += 0.25 if ch == "SP500" else 0.35

        btc_series = st.session_state.get("returns_btc", [])
        btc_ns = neg_streak(btc_series, r - 1, window=3)
        if btc_ns >= 2 and ch in ("SP500", "GOLD"):
            bonuses += 0.25

        if (not lev) and ns >= 2:
            bonuses += 0.12

    if switch_rate > 0.55:
        penalties += (switch_rate - 0.55) * 3.0

    if concentration > 0.55 and share["BTC"] > 0.5:
        penalties += 1.0

    rationality = 84.0 - 6.5 * penalties + 3.0 * bonuses
    if risk > 80:
        rationality -= (risk - 80) * 0.25

    rationality = int(max(0, min(100, round(rationality))))

    notes = [
        f"Udział wyborów: BTC {share['BTC']:.0%}, Złoto {share['GOLD']:.0%}, S&P 500 {share['SP500']:.0%}, Gotówka {share['CASH']:.0%}.",
        f"Lewar użyty w {share_lev:.0%} rund.",
        f"Częstotliwość zmian instrumentu: {switch_rate:.0%} (im wyżej, tym większe ryzyko overtradingu).",
        f"Koncentracja portfela: {concentration:.2f} (im wyżej, tym mniej dywersyfikacji).",
    ]
    return {"risk": risk, "rationality": rationality, "notes": notes}

def render_summary_cards(items):
    # ✅ render jak na screenie + pewne HTML (bez bloków kodu)
    cards = []
    for it in items:
        delta = it["delta_pct"]
        delta_class = "delta-pos" if delta >= 0 else "delta-neg"
        card = f"""
<div class="summary-card">
  <div class="summary-title">{it['title']}</div>
  <div class="summary-value">{it['value_num_str']} <span class="summary-ccy">PLN</span></div>
  <div class="summary-delta"><span class="{delta_class}">{fmt_pct(delta)}</span></div>
</div>
"""
        cards.append(textwrap.dedent(card).strip())

    html = '<div class="summary-grid">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)

# --- STRONY ---
def show_game1_intro():
    st.header("Gra Inwestycyjna")

    st.markdown("""
<div class="instruction-card">
    <h3>Instrukcja:</h3>
    Masz <b>40 rund</b>. Startujesz z <b>10 000 PLN</b>.
    W każdej rundzie wybierasz instrument na kolejny miesiąc:
    <ul>
        <li><b>S&P 500</b> — niższe/średnie ryzyko</li>
        <li><b>Złoto</b> — średnie ryzyko</li>
        <li><b>Bitcoin</b> — wysokie ryzyko</li>
        <li><b>Gotówka</b> — 0% (bezpieczna przystań)</li>
    </ul>
    <div class="important-text">Cel: maksymalizacja wyniku.</div>
    Od 20. rundy dostępny będzie <b>Lewar (x2)</b>.
    Zwroty są losowe, z lekką „pamięcią” trendu i rzadkimi skokami (w zależności od instrumentu).
</div>
    """, unsafe_allow_html=True)

    if "g1_round" not in st.session_state:
        init_game_state()

    if st.button("Start gry", use_container_width=True):
        next_page("game1")

def show_game1():
    current_idx = st.session_state.g1_round
    if current_idx >= TOTAL_ROUNDS - 1:
        next_page("game1_summary")
        return

    current_cap = st.session_state.g1_history_user[-1]
    prev_cap = st.session_state.g1_history_user[-2] if len(st.session_state.g1_history_user) > 1 else 10000.0
    pct_change_show = ((current_cap - prev_cap) / prev_cap) * 100

    label = LABELS_TEXT[current_idx] if current_idx < len(LABELS_TEXT) else f"R{current_idx+1}"
    st.subheader(f"Runda {current_idx + 1} / {TOTAL_ROUNDS} ({label})")

    st.metric("Twój Kapitał", f"{fmt_pln_num(current_cap)} PLN", fmt_pct(pct_change_show))

    chart_data = pd.DataFrame({
        "S&P 500": pad_history(st.session_state.hist_sp, TOTAL_ROUNDS),
        "Złoto": pad_history(st.session_state.hist_gold, TOTAL_ROUNDS),
        "Bitcoin": pad_history(st.session_state.hist_btc, TOTAL_ROUNDS),
        "Twój Kapitał": pad_history(st.session_state.g1_history_user, TOTAL_ROUNDS)
    })
    st.line_chart(chart_data.iloc[:TOTAL_ROUNDS])

    leverage_active = False
    if current_idx >= 20:
        st.warning("⚡ ODBLOKOWANO DŹWIGNIĘ (LEWAR x2)")
        leverage_active = st.checkbox("Użyj dźwigni (x2 zyski/straty)")

    st.write("W co inwestujesz na kolejny miesiąc?")
    col1, col2, col3, col4 = st.columns(4)

    choice = None
    if col1.button(INSTRUMENTS["SP500"]["label"], use_container_width=True):
        choice = "SP500"
    if col2.button(INSTRUMENTS["GOLD"]["label"], use_container_width=True):
        choice = "GOLD"
    if col3.button(INSTRUMENTS["BTC"]["label"], use_container_width=True):
        choice = "BTC"
    if col4.button(INSTRUMENTS["CASH"]["label"], use_container_width=True):
        choice = "CASH"

    if choice:
        next_round = current_idx + 1
        ensure_round_returns(next_round)
        apply_benchmarks(next_round)

        if choice == "SP500":
            user_ret = st.session_state.returns_sp[next_round - 1]
        elif choice == "GOLD":
            user_ret = st.session_state.returns_gold[next_round - 1]
        elif choice == "BTC":
            user_ret = st.session_state.returns_btc[next_round - 1]
        else:
            user_ret = 0.0

        if leverage_active:
            user_ret *= 2
            if choice in ("SP500", "GOLD"):
                user_ret = clamp(user_ret, -0.25, 0.25)
            elif choice == "BTC":
                user_ret = clamp(user_ret, -0.55, 0.55)

        new_cap = current_cap * (1 + user_ret)

        st.session_state.g1_history_user.append(new_cap)
        st.session_state.g1_round += 1
        st.session_state.g1_capital = new_cap

        st.session_state.g1_decisions.append({
            "round": next_round,
            "choice": choice,
            "leverage": leverage_active,
            "return": user_ret,
            "capital": new_cap
        })

        st.rerun()

def show_game1_summary():
    st.header("Podsumowanie Gry Inwestycyjnej")

    start_cap = 10000.0
    end_cap = st.session_state.g1_history_user[-1]
    user_ret_pct = ((end_cap - start_cap) / start_cap) * 100

    sp_end = st.session_state.hist_sp[-1]
    gold_end = st.session_state.hist_gold[-1]
    btc_end = st.session_state.hist_btc[-1]

    sp_ret = (sp_end / 10000.0 - 1) * 100
    gold_ret = (gold_end / 10000.0 - 1) * 100
    btc_ret = (btc_end / 10000.0 - 1) * 100

    # ✅ kafelki jak na screenie
    render_summary_cards([
        {"title": "Twój Wynik", "value_num_str": fmt_pln_num(end_cap), "delta_pct": user_ret_pct},
        {"title": "S&P 500", "value_num_str": fmt_pln_num(sp_end), "delta_pct": sp_ret},
        {"title": "Złoto", "value_num_str": fmt_pln_num(gold_end), "delta_pct": gold_ret},
        {"title": "Bitcoin", "value_num_str": fmt_pln_num(btc_end), "delta_pct": btc_ret},
    ])

    # ✅ reszta: wraca dokładnie jak w “dobrym końcu gry”
    st.markdown("---")
    chart_data = pd.DataFrame({
        "S&P 500": pad_history(st.session_state.hist_sp, TOTAL_ROUNDS),
        "Złoto": pad_history(st.session_state.hist_gold, TOTAL_ROUNDS),
        "Bitcoin": pad_history(st.session_state.hist_btc, TOTAL_ROUNDS),
        "Twój Kapitał": pad_history(st.session_state.g1_history_user, TOTAL_ROUNDS)
    })
    st.line_chart(chart_data)

    st.markdown("---")
    st.subheader("Twoje decyzje")
    if st.session_state.g1_decisions:
        df_dec = pd.DataFrame(st.session_state.g1_decisions)
        map_choice = {"SP500": "S&P 500", "GOLD": "Złoto", "BTC": "Bitcoin", "CASH": "Gotówka"}
        df_dec["Instrument"] = df_dec["choice"].map(map_choice)
        df_dec["Lewar"] = df_dec["leverage"].map({True: "Tak", False: "Nie"})
        df_dec["Zwrot %"] = (df_dec["return"] * 100).round(2)
        df_dec["Kapitał (PLN)"] = df_dec["capital"].round(2)
        df_dec = df_dec[["round", "Instrument", "Lewar", "Zwrot %", "Kapitał (PLN)"]].rename(columns={"round": "Runda"})
        st.dataframe(df_dec, use_container_width=True)

    st.markdown("---")
    st.subheader("Ocena inwestora")
    scores = compute_player_scores()
    st.info(investor_sentence(scores["rationality"], scores["risk"]))

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Racjonalność (0–100)", scores["rationality"])
    with c2:
        st.metric("Skłonność do ryzyka (0–100)", scores["risk"])

    st.markdown("**Dlaczego taka ocena?**")
    st.markdown("""
- **Racjonalność spada**, jeśli często trzymasz instrument, który ma **serię spadków** oraz jeśli używasz **lewara po spadkach**.  
- Dodatkowo racjonalność spada przy **overtradingu** (zbyt częste zmiany) oraz przy „**kupowaniu po euforii**” (wejście po dużym wzroście).  
- **Skłonność do ryzyka rośnie**, jeśli często wybierasz **Bitcoin** i/lub używasz **lewara**, a spada przy częstej **gotówce** oraz (lekko) przy częstym **S&P 500**.  
- Wliczamy też **koncentrację** (jeśli prawie zawsze jedno aktywo, zwłaszcza ryzykowne).
""")

    for n in scores["notes"]:
        st.write("• " + n)

    st.markdown("---")
    if st.button("Zagraj ponownie (reset)", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("g1_") or k.startswith("hist_") or k.startswith("returns_"):
                del st.session_state[k]
        init_game_state()
        st.session_state.page = "game1_intro"
        st.rerun()

# Router stron aplikacji
if st.session_state.page == "game1_intro":
    show_game1_intro()
elif st.session_state.page == "game1":
    show_game1()
elif st.session_state.page == "game1_summary":
    show_game1_summary()



