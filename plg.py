import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 📐 Gewicht auf 2.5 kg Schritte runden
def round_to_2_5(weight):
    return round(weight / 2.5) * 2.5

# 🧮 Satz-/Intensitätslogik je Trainingstag
def calculate_week_plan(lift_name, one_rm, week, tag, deload=False):
    plan = []

    if deload:
        intensities = [0.60]          # Deload: 60% 1RM
        reps_sets = [(2, 3)]          # 2 Wdh x 3 Sätze (leicht)
    else:
        if tag == 1:                  # Tag 1: schwer
            intensities = [0.85, 0.70]
            reps_sets = [(3, 3), (5, 2)]
        elif tag == 2:                # Tag 2: Zusatzübungen
            intensities = [0.70, 0.65]
            reps_sets = [(6, 3), (8, 3)]
        elif tag == 3:                # Tag 3: Volumen/Technik
            intensities = [0.75, 0.65]
            reps_sets = [(5, 4), (8, 3)]

    for (reps, sets), intensity in zip(reps_sets, intensities):
        weight = round_to_2_5(one_rm * intensity)
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

# 📈 Diagrammdaten (Top-Satz je Woche)
def generate_chart_data(lift_name, one_rm, weeks=16, progression=0.02, deload_every=8):
    data = []
    for week in range(1, weeks + 1):
        is_deload = (week % deload_every == 0)
        # einfache progressive Steigerung des 1RM (optional)
        adjusted_week = week - 1 if not is_deload else week - 2
        current_max = one_rm * (1 + progression) ** max(adjusted_week, 0)
        top_intensity = 0.85 if not is_deload else 0.60
        top_set = round_to_2_5(current_max * top_intensity)
        data.append((week, top_set))
    return pd.DataFrame(data, columns=["Woche", lift_name])

# 🖥 UI
st.set_page_config(page_title="Powerlifting Trainingsplan", layout="centered")
st.title("🏋️‍♂️ Powerlifting Trainingsplan Generator")

with st.form("input_form"):
    st.subheader("🔢 Eingabe deiner 1RM-Werte (5 kg Schritte)")
    # Hauptlifts
    sq = st.number_input("Squat (kg)", min_value=30.0, value=180.0, step=5.0)
    bp = st.number_input("Bench Press (kg)", min_value=30.0, value=120.0, step=5.0)
    dl = st.number_input("Deadlift (kg)", min_value=50.0, value=200.0, step=5.0)
    # Zusatzübungen (Tag 2)
    mp = st.number_input("Military Press (kg)", min_value=20.0, value=60.0, step=5.0)
    br = st.number_input("Barbell Row (kg)", min_value=20.0, value=80.0, step=5.0)
    dp = st.number_input("Dips (kg)", min_value=10.0, value=40.0, step=5.0)

    st.subheader("📅 Planparameter")
    start_week = st.number_input("Startwoche", min_value=1, value=1, step=1)
    weeks_total = st.number_input("Anzahl Wochen", min_value=1, value=4, step=1)
    deload_every = st.number_input("Deload alle X Wochen", min_value=4, value=8, step=1)
    progression = st.number_input("Wöchentliche 1RM-Progression (%)", min_value=0.0, value=2.0, step=0.5, help="Prozent pro Woche (optional)")
    submitted = st.form_submit_button("📤 Plan generieren")

if not submitted:
    st.info("Fülle die Eingaben aus und klicke auf „📤 Plan generieren“, um den Plan zu erstellen.")

if submitted:
    # einfache Validierung
    inputs = {"Squat": sq, "Bench Press": bp, "Deadlift": dl, "Military Press": mp, "Barbell Row": br, "Dips": dp}
    missing = [name for name, val in inputs.items() if val is None]
    if missing:
        st.error(f"Es fehlen Eingabewerte: {', '.join(missing)}")
        st.stop()

    all_weeks = []
    for w in range(start_week, start_week + int(weeks_total)):
        deload = (w % int(deload_every) == 0)

        # Tag 1: Hauptübungen schwer
        all_weeks.append(calculate_week_plan("Squat", sq, w, tag=1, deload=deload))
        all_weeks.append(calculate_week_plan("Bench Press", bp, w, tag=1, deload=deload))
        all_weeks.append(calculate_week_plan("Deadlift", dl, w, tag=1, deload=deload))

        # Tag 2: Zusatzübungen
        all_weeks.append(calculate_week_plan("Military Press", mp, w, tag=2, deload=deload))
        all_weeks.append(calculate_week_plan("Barbell Row", br, w, tag=2, deload=deload))
        all_weeks.append(calculate_week_plan("Dips", dp, w, tag=2, deload=deload))

        # Tag 3: Hauptübungen Volumen/Technik
        all_weeks.append(calculate_week_plan("Squat", sq, w, tag=3, deload=deload))
        all_weeks.append(calculate_week_plan("Bench Press", bp, w, tag=3, deload=deload))
        all_weeks.append(calculate_week_plan("Deadlift", dl, w, tag=3, deload=deload))

    # Zusammenführen und sortieren
    full_plan = (
        pd.concat(all_weeks)
        .sort_values(by=["Woche", "Tag", "Übung"])
        .reset_index(drop=True)
    )

    st.subheader("📅 Trainingsplan")
    st.dataframe(full_plan)

    # Diagramme
    st.subheader("📈 Progression der Top-Sätze")
    prog = progression / 100.0
    chart_sq = generate_chart_data("Squat", sq, weeks=int(weeks_total), progression=prog, deload_every=int(deload_every))
    chart_bp = generate_chart_data("Bench Press", bp, weeks=int(weeks_total), progression=prog, deload_every=int(deload_every))
    chart_dl = generate_chart_data("Deadlift", dl, weeks=int(weeks_total), progression=prog, deload_every=int(deload_every))
    chart_mp = generate_chart_data("Military Press", mp, weeks=int(weeks_total), progression=prog, deload_every=int(deload_every))
    chart_br = generate_chart_data("Barbell Row", br, weeks=int(weeks_total), progression=prog, deload_every=int(deload_every))
    chart_dp = generate_chart_data("Dips", dp, weeks=int(weeks_total), progression=prog, deload_every=int(deload_every))

    chart_data = pd.concat([
        chart_sq.set_index("Woche"),
        chart_bp.set_index("Woche"),
        chart_dl.set_index("Woche"),
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

    # Excel-Export
    st.subheader("📥 Export")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        full_plan.to_excel(writer, sheet_name="Wochenplan", index=False)
        chart_data.reset_index().to_excel(writer, sheet_name="Diagramm", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Diagramm"]
        chart = workbook.add_chart({'type': 'line'})
        names = ["Squat", "Bench Press", "Deadlift", "Military Press", "Barbell Row", "Dips"]
        for i, name in enumerate(names):
            chart.add_series({
                'name':       ['Diagramm', 0, i + 1],
                'categories': ['Diagramm', 1, 0, int(weeks_total), 0],
                'values':     ['Diagramm', 1, i + 1, int(weeks_total), i + 1],
            })
        chart.set_title({'name': 'Progression der Top-Sätze'})
        chart.set_x_axis({'name': 'Woche'})
        chart.set_y_axis({'name': 'Gewicht (kg)'})
        chart.set_style(10)
        worksheet.insert_chart('F2', chart)

    st.download_button(
        label="📥 Excel-Datei herunterladen",
        data=output.getvalue(),
        file_name=f"Trainingsplan_Woche_{start_week}_bis_{start_week+int(weeks_total)-1}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
