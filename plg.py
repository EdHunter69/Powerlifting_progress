import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 📐 Gewicht auf nächsthöheres 2.5 kg runden
def round_up_to_2_5(weight):
    return round(weight / 2.5) * 2.5

# 📊 Trainingsplan für eine Woche berechnen
def calculate_week_plan(lift_name, one_rm, week, tag, deload=False):
    plan = []
    if deload:
        intensities = [0.60]  # Deload bei 60% 1RM
        reps_sets = [(3, 2)]
    else:
        if tag == 1:  # Tag 1 = schwer
            intensities = [0.85, 0.70]  # schwer + moderat
            reps_sets = [(3, 3), (2, 5)]
        elif tag == 2:  # Tag 2 = Zusatzübungen
            intensities = [0.70, 0.65]
            reps_sets = [(3, 6), (3, 8)]
        elif tag == 3:  # Tag 3 = Volumen/Technik
            intensities = [0.75, 0.65]
            reps_sets = [(4, 5), (3, 8)]

    for (sets, reps), intensity in zip(reps_sets, intensities):
        weight = round_up_to_2_5(one_rm * intensity)
        plan.append({
            "Woche": week,
            "Tag": tag,
            "Übung": lift_name,
            "Sätze": sets,
            "Wdh": reps,
            "Intensität (%)": int(intensity * 100),
            "Gewicht (kg)": weight,
            "Deload": "Ja" if deload else "Nein"
        })
    return pd.DataFrame(plan)

# 📈 Diagrammdaten generieren
def generate_chart_data(lift_name, one_rm, weeks=16, progression=0.02, deload_every=8):
    data = []
    for week in range(1, weeks + 1):
        is_deload = (week % deload_every == 0)
        adjusted_week = week - 1 if not is_deload else week - 2
        current_max = one_rm * (1 + progression) ** adjusted_week
        top_set = round_up_to_2_5(current_max * (0.85 if not is_deload else 0.60))
        data.append((week, top_set))
    return pd.DataFrame(data, columns=["Woche", lift_name])

# 🖥 Streamlit UI
st.set_page_config(page_title="Powerlifting Trainingsplan", layout="centered")
st.title("🏋️‍♂️ Powerlifting Trainingsplan Generator")

with st.form("input_form"):
    st.subheader("🔢 Eingabe deiner 1RM-Werte (nur 5kg Schritte)")
    sq = st.number_input("Squat (kg)", min_value=30.0, value=180.0, step=5.0)
    bp = st.number_input("Bench Press (kg)", min_value=30.0, value=120.0, step=5.0)
    dl = st.number_input("Deadlift (kg)", min_value=50.0, value=200.0, step=5.0)
    mp = st
