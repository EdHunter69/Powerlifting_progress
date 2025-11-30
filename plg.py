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
        if tag in [1, 3]:  # Haupttage: Squat, Bench, Deadlift
            intensities = [0.85, 0.70]  # schwer + moderat
            reps_sets = [(3, 3), (2, 5)]
        elif tag == 2:  # Zusatzübungen
            intensities = [0.70, 0.65]
            reps_sets = [(3, 6), (3, 8)]

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
    st.subheader("🔢 Eingabe deiner 1RM-Werte")
    sq = st.number_input("Squat (kg)", min_value=30.0, value=180.0)
    bp = st.number_input("Bench Press (kg)", min_value=30.0, value=120.0)
    dl = st.number_input("Deadlift (kg)", min_value=50.0, value=200.0)
    mp = st.number_input("Military Press (kg)", min_value=20.0, value=60.0)
    br = st.number_input("Barbell Row (kg)", min_value=20.0, value=80.0)
    dp = st.number_input("Dips (kg)", min_value=10.0, value=40.0)
    start_week = st.number_input("Startwoche", min_value=1, value=1)
    weeks_total = st.number_input("Anzahl Wochen", min_value=1, value=4)
    submitted = st.form_submit_button("📤 Plan generieren")

if submitted:
    all_weeks = []
    for w in range(start_week, start_week + weeks_total):
        deload = (w % 8 == 0)

        # Tag 1: Grundübungen
        all_weeks.append(calculate_week_plan("Squat", sq, w, tag=1, deload=deload))
        all_weeks.append(calculate_week_plan("Bench Press", bp, w, tag=1, deload=deload))
        all_weeks.append(calculate_week_plan("Deadlift", dl, w, tag=1, deload=deload))

        # Tag 2: Zusatzübungen
        all_weeks.append(calculate_week_plan("Military Press", mp, w, tag=2, deload=deload))
        all_weeks.append(calculate_week_plan("Barbell Row", br, w, tag=2, deload=deload))
        all_weeks.append(calculate_week_plan("Dips", dp, w, tag=2, deload=deload))

        # Tag 3: Grundübungen
        all_weeks.append(calculate_week_plan("Squat", sq, w, tag=3, deload=deload))
        all_weeks.append(calculate_week_plan("Bench Press", bp, w, tag=3, deload=deload))
        all_weeks.append(calculate_week_plan("Deadlift", dl, w, tag=3, deload=deload))

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
    chart_sq = generate_chart_data("Squat", sq, weeks_total)
    chart_bp = generate_chart_data("Bench Press", bp, weeks_total)
    chart_dl = generate_chart_data("Deadlift", dl, weeks_total)
    chart_mp = generate_chart_data("Military Press", mp, weeks_total)
    chart_br = generate_chart_data("Barbell Row", br, weeks_total)
    chart_dp = generate_chart_data("Dips", dp, weeks_total)

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

    # 📤 Excel-Datei zum Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        full_plan.to_excel(writer, sheet_name="Wochenplan", index=False)
        chart_data.reset_index().to_excel(writer, sheet_name="Diagramm", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Diagramm"]
        chart = workbook.add_chart({'type': 'line'})
        for i, name in enumerate(["Squat", "Bench Press", "Deadlift",
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
