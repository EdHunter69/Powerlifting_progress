import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

def round_up_to_2_5(weight):
    return ((weight + 2.5 - 1e-6) // 2.5 + 1) * 2.5

def calculate_week_plan(exercise_name, max_weight, week, tag, progression=0.02, deload_every=8):
    is_deload = (week % deload_every == 0)
    adjusted_week = week - 1 if not is_deload else week - 2
    current_max = max_weight * (1 + progression) ** adjusted_week

    if is_deload:
        sessions = [{"reps": 3, "sets": 2, "intensity": 0.60}]
    else:
        if tag == 1:  # Day 1 - Higher intensity, lower volume
            sessions = [
                {"reps": 2, "sets": 1, "intensity": 0.85},
                {"reps": 4, "sets": 3, "intensity": 0.70}
            ]
        elif tag == 3:  # Day 3 - Moderated intensity, higher volume / technical focus
            sessions = [
                {"reps": 3, "sets": 1, "intensity": 0.75},
                {"reps": 6, "sets": 4, "intensity": 0.65}
            ]
        elif tag == 2:  # Day 2 remains the same, for accessory work
            sessions = [
                {"reps": 8, "sets": 3, "intensity": 0.65},
                {"reps": 10, "sets": 2, "intensity": 0.60}
            ]

    plan = []
    for s in sessions:
        gewicht = round_up_to_2_5(current_max * s["intensity"])
        plan.append({
            "Woche": week,
            "Tag": tag,
            "Übung": exercise_name,
            "Sätze": s["sets"],
            "Wdh": s["reps"],
            "Intensität (%)": int(s["intensity"] * 100),
            "Gewicht (kg)": gewicht,
            "Deload": "Ja" if is_deload else "Nein"
        })
    return pd.DataFrame(plan)

# Remaining code block unchanged
