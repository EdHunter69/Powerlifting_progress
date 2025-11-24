import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 📐 Gewicht auf nächsthöheres 2.5 kg runden
def round_up_to_2_5(weight):
    return ((weight + 2.5 - 1e-6) // 2.5 + 1) * 2.5

# 📊 Trainingsplan für eine Woche berechnen
def calculate_week_plan(exercise_name, max_weight, week, tag, progression=0.02, deload_every=8):
    is_deload = (week % deload_every == 0)
    adjusted_week = week - 1 if not is_deload else week - 2
    current_max = max_weight * (1 + progression) ** adjusted_week

    if is_deload:
        sessions = [{"reps": 3, "sets": 2, "intensity": 0.60}]
    else:
        if tag in [1, 3]:  # Tag 1 und 3 = Grundübungen
            sessions = [
                {"reps": 2, "sets": 1, "intensity": 0.80},
                {"reps": 5, "sets": 4, "intensity": 0.65}
            ]
        elif tag == 2:  # Tag 2 = Zusatzübungen
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

# 📈 Diagrammdaten generieren
def generate_chart_data(exercise_name, max_weight, weeks=16, progression=0.02, deload_every=8):
    data = []
    for week in range(1, weeks + 1):
        is_deload = (week % deload_every == 0)
        adjusted_week = week - 1 if not is_deload else week - 2
        current_max = max_weight * (1 + progression) ** adjusted_week
        top_set = round_up_to_2_5(current_max * (0.60 if is_deload else 0.80))
        data.append((week, top_set))
    return pd.DataFrame(data, columns=["Woche", exercise_name])

# 🖥 Streamlit UI
st.set_page_config(page_title="Trainingsplan Generator", layout="centered")
st.title("🏋️‍♂️ Trainingsplan Generator")

with st.form("input_form"):
    st.subheader("🔢 Eingabe deiner Maximalkraftwerte")
    dl = st.number_input("Kreuzheben (kg)", min_value=50.0, value=180.0)
    bp = st.number_input("Bankdrücken (kg)", min_value=30.0, value=120.0)
    sq = st.number_input("Kniebeuge (kg)", min_value=30.0, value=100.0)
    mp = st.number_input("Military Press (kg)", min_value=20.0, value=60.0)
    br = st.number_input("Barbell Row (kg)", min_value=20.0, value=80.0)
    dp = st.number_input("Dips (kg)", min_value=10.0, value=40.0)
    start_week = st.number_input("Startwoche", min_value=1, value=1)
    weeks_total = st.number_input("Anzahl Wochen", min_value=1, value=4)
    submitted = st.form_submit_button("📤 Plan generieren")

if submitted:
    all_weeks = []
    for w in range(start_week, start_week + weeks_total):
        # Tag 1: Grundübungen
        all_weeks.append(calculate_week_plan("Kreuzheben", dl, w, tag=1))
        all_weeks.append(calculate_week_plan("Bankdrücken", bp, w, tag=1))
        all_weeks.append(calculate_week_plan("Kniebeuge", sq, w, tag=1))

        # Tag 2: Zusatzübungen
        all_weeks.append(calculate_week_plan("Military Press", mp, w, tag=2))
        all_weeks.append(calculate_week_plan("Barbell Row", br, w, tag=2))
        all_weeks.append(calculate_week_plan("Dips", dp, w, tag=2))

        # Tag 3: Grundübungen
        all_weeks.append(calculate_week_plan("Kreuzheben", dl, w, tag=3))
        all_weeks.append(calculate_week_plan("Bankdrücken", bp, w, tag=3))
        all_weeks.append(calculate_week_plan("Kniebeuge", sq, w, tag=3))

    # Sortierung: Woche → Tag → Übung
    full_plan = (
        pd.concat(all_weeks)
        .sort_values(by=["Woche", "Tag", "Übung"])
        .reset_index(drop=True)
    )

    st.subheader("📅 Trainingsplan")
    st.dataframe(full_plan)

    # 📈 Diagramm anzeigen
    st.subheader("📈 Progression der Top-Sätze")
    chart_dl = generate_chart_data("Kreuzheben", dl, weeks_total)
    chart_bp = generate_chart_data("Bankdrücken", bp, weeks_total)
    chart_sq = generate_chart_data("Kniebeuge", sq, weeks_total)
    chart_mp = generate_chart_data("Military Press", mp, weeks_total)
    chart_br = generate_chart_data("Barbell Row", br, weeks_total)
    chart_dp = generate_chart_data("Dips", dp, weeks_total)

    chart_data = pd.concat([
        chart_dl.set_index("Woche"),
        chart_bp.set_index("Woche"),
        chart_sq.set_index("Woche"),
        chart_mp.set_index("Woche"),
        chart_br.set_index("Woche"),
        chart_dp.set_index("Woche")
    ], axis=1)

    fig, ax = plt.subplots()
    chart_data.plot(ax=ax, marker='o')
    ax.set_title("Progression der Top-Sätze")
    ax.set_xlabel("Woche")
    ax.set_ylabel("Gewicht (kg)")
    ax.grid(True)
    st.pyplot(fig)

    # 📤 Excel-Datei zum Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        full_plan.to_excel(writer, sheet_name="Wochenplan", index=False)
        chart_data.reset_index().to_excel(writer, sheet_name="Diagramm", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Diagramm"]
        chart = workbook.add_chart({'type': 'line'})
        for i, name in enumerate(["Kreuzheben", "Bankdrücken", "Kniebeuge",
                                  "Military Press", "Barbell Row", "Dips"]):
            chart.add_series({
                'name':       ['Diagramm', 0, i + 1],
                'categories': ['Diagramm', 1, 0, weeks_total, 0],
                'values':     ['Diagramm', 1, i + 1, weeks_total, i + 1],
            })
        chart.set_title({'name': 'Progression der Top-Sätze'})
        chart.set_x_axis({'name': 'Woche'})
        chart.set_y_axis({'name': 'Gewicht (kg)'})
        chart.set_style(10)
        worksheet.insert_chart('F2', chart)

    st.download_button(
        label="📥 Excel-Datei herunterladen",
        data=output.getvalue(),
        file_name=f"Trainingsplan_Woche_{start_week}_bis_{start_week+weeks_total-1}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
