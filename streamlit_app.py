import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="WR Success Predictor", layout="wide")

st.title("📊 WR Success Predictor (PPR)")
st.markdown("Predict if a WR will become top-36 fantasy based on rookie + Year 2 stats")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Rookie Season Stats")
    rookie_receptions = st.number_input("Receptions (Yr 1)", min_value=0, max_value=200, value=50)
    rookie_yards = st.number_input("Receiving Yards (Yr 1)", min_value=0, max_value=2000, value=600)
    rookie_tds = st.number_input("TDs (Yr 1)", min_value=0, max_value=20, value=4)
    draft_round = st.selectbox("Draft Round", [1, 2, 3, 4, 5, 6, 7, "UDFA"])

with col2:
    st.subheader("Year 2 Stats")
    yr2_receptions = st.number_input("Receptions (Yr 2)", min_value=0, max_value=200, value=70)
    yr2_yards = st.number_input("Receiving Yards (Yr 2)", min_value=0, max_value=2000, value=900)
    yr2_tds = st.number_input("TDs (Yr 2)", min_value=0, max_value=20, value=6)
    games_played = st.number_input("Games Played (Yr 1 + 2)", min_value=0, max_value=32, value=28)

# Calculate features
rookie_ppg = ((rookie_receptions + rookie_tds * 6) / max(games_played / 2, 1)) if games_played > 0 else 0
yr2_ppg = ((yr2_receptions + yr2_tds * 6) / max(games_played / 2, 1)) if games_played > 0 else 0
ppg_growth = yr2_ppg - rookie_ppg
volume_growth = ((yr2_receptions - rookie_receptions) / max(rookie_receptions, 1)) * 100 if rookie_receptions > 0 else 0
efficiency = (yr2_yards / max(yr2_receptions, 1)) if yr2_receptions > 0 else 0

draft_score = {"1": 10, "2": 8, "3": 6, "4": 4, "5": 2, "6": 1, "7": 0.5, "UDFA": 0}.get(str(draft_round), 0)

# Success prediction (heuristic scoring)
score = 0
signals = []

# Draft capital (20 pts)
score += draft_score * 2
if draft_score >= 8:
    signals.append("✅ High draft capital — strong indicator")
elif draft_score == 0:
    signals.append("⚠️ UDFA — will need elite stats to overcome")

# Year 1 volume (20 pts)
if rookie_receptions >= 50:
    score += 15
    signals.append("✅ Strong rookie volume (50+ catches)")
elif rookie_receptions >= 30:
    score += 10
    signals.append("⚠️ Moderate rookie volume")
else:
    signals.append("🚩 Low rookie volume — red flag")

# Year 2 growth (20 pts)
if volume_growth >= 30:
    score += 15
    signals.append("✅ Strong growth Year 1→2 (30%+)")
elif volume_growth >= 0:
    score += 8
    signals.append("⚠️ Flat volume — concerning")
else:
    signals.append("🚩 Volume declined — major red flag")

# Efficiency (20 pts)
if efficiency >= 8.5:
    score += 15
    signals.append("✅ Elite efficiency (8.5+ Y/R)")
elif efficiency >= 7.5:
    score += 10
    signals.append("⚠️ Good efficiency")
else:
    signals.append("⚠️ Below-average efficiency")

# Year 2 PPG (20 pts)
if yr2_ppg >= 12:
    score += 15
    signals.append("✅ Elite Year 2 PPG (12+)")
elif yr2_ppg >= 8:
    score += 10
    signals.append("⚠️ Solid Year 2 PPG")
else:
    signals.append("⚠️ Low Year 2 PPG")

# Durability (contingent)
if games_played >= 28:
    score += 3
    signals.append("✅ Durable (28+ games)")
else:
    signals.append("⚠️ Injury concern — limited sample")

# Calculate probability
success_prob = min(100, (score / 100) * 100)

# Display results
st.divider()
st.subheader("📈 Prediction")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Success Probability", f"{success_prob:.1f}%")
with col2:
    st.metric("Year 1 PPG (PPR)", f"{rookie_ppg:.1f}")
with col3:
    st.metric("Year 2 PPG (PPR)", f"{yr2_ppg:.1f}")

st.divider()
st.subheader("🎯 Key Signals")
for signal in signals:
    st.write(signal)

# Interpretation
st.divider()
if success_prob >= 75:
    st.success("🔥 **Strong candidate for top-36** — Early indicators align with sustained success")
elif success_prob >= 60:
    st.info("📊 **Moderate prospect** — Some strong signals but execution risk remains")
elif success_prob >= 40:
    st.warning("⚠️ **Risky pick** — Inconsistent signals or low draft capital")
else:
    st.error("🚫 **Unlikely to sustain** — Major red flags or insufficient volume")
