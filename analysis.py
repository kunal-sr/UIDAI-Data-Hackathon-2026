# ======================================================
# UIDAI DATA HACKATHON 2026
# Aadhaar ENROLMENT DATA ANALYSIS (FINAL)
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
import os

# ======================================================
# 1. LOAD ENROLMENT DATA
# ======================================================

enrolment_files = [
    "api_data_aadhar_enrolment_0_500000.csv",
    "api_data_aadhar_enrolment_500000_1000000.csv",
    "api_data_aadhar_enrolment_1000000_1006029.csv"
]

# Safety check
for f in enrolment_files:
    if not os.path.exists(f):
        raise FileNotFoundError(f"Missing file: {f}")

df = pd.concat([pd.read_csv(f) for f in enrolment_files], ignore_index=True)

print("Total Enrolment Records Loaded:", len(df))

# ======================================================
# 2. CLEAN & STANDARDISE STATE NAMES
# ======================================================

df["state_clean"] = df["state"].str.lower().str.strip()

state_fix_map = {
    "orissa": "odisha",
    "pondicherry": "puducherry",
    "west bangal": "west bengal",
    "westbengal": "west bengal",
    "west  bengal": "west bengal",
    "jammu & kashmir": "jammu and kashmir",
    "andaman & nicobar islands": "andaman and nicobar islands",
    "dadra & nagar haveli": "dadra and nagar haveli and daman and diu",
    "daman and diu": "dadra and nagar haveli and daman and diu",
    "daman & diu": "dadra and nagar haveli and daman and diu",
    "dadra and nagar haveli": "dadra and nagar haveli and daman and diu",
    "the dadra and nagar haveli and daman and diu":
        "dadra and nagar haveli and daman and diu",
    "100000": None
}

df["state_clean"] = df["state_clean"].replace(state_fix_map)
df = df[df["state_clean"].notna()]

# ======================================================
# 3. FILTER TO OFFICIAL 37 STATES & UTs
# ======================================================

official_states_uts = {
    # States (28)
    "andhra pradesh","arunachal pradesh","assam","bihar","chhattisgarh",
    "goa","gujarat","haryana","himachal pradesh","jharkhand","karnataka",
    "kerala","madhya pradesh","maharashtra","manipur","meghalaya","mizoram",
    "nagaland","odisha","punjab","rajasthan","sikkim","tamil nadu",
    "telangana","tripura","uttar pradesh","uttarakhand","west bengal",

    # Union Territories (9)
    "andaman and nicobar islands","chandigarh",
    "dadra and nagar haveli and daman and diu",
    "delhi","jammu and kashmir","ladakh",
    "lakshadweep","puducherry"
}

df = df[df["state_clean"].isin(official_states_uts)]

print("Official States & UTs Count:", df["state_clean"].nunique())

# ======================================================
# 4. FEATURE ENGINEERING
# ======================================================

age_cols = ["age_0_5", "age_5_17", "age_18_greater"]
df["total_enrolments"] = df[age_cols].sum(axis=1)

# ======================================================
# 5. BAR CHART: TOP & BOTTOM STATES
# ======================================================

state_summary = (
    df.groupby("state_clean")["total_enrolments"]
    .sum()
    .reset_index()
    .sort_values(by="total_enrolments", ascending=False)
)

top10 = state_summary.head(10)
bottom10 = state_summary.tail(10)

# --- Top 10 ---
plt.figure(figsize=(10,5))
bars = plt.bar(top10["state_clean"], top10["total_enrolments"])
plt.xticks(rotation=45, ha="right")
plt.title("Top 10 States by Aadhaar Enrolment")
plt.ylabel("Total Enrolments")
plt.ticklabel_format(style="plain", axis="y")

for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x()+bar.get_width()/2, h, f"{int(h):,}",
             ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.show()

# --- Bottom 10 ---
plt.figure(figsize=(10,5))
bars = plt.bar(bottom10["state_clean"], bottom10["total_enrolments"])
plt.xticks(rotation=45, ha="right")
plt.title("Bottom 10 States / UTs by Aadhaar Enrolment")
plt.ylabel("Total Enrolments")
plt.ticklabel_format(style="plain", axis="y")

for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x()+bar.get_width()/2, h, f"{int(h):,}",
             ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.show()

# ======================================================
# 6. PIE CHART: AGE GROUP DISTRIBUTION
# ======================================================

age_totals = df[age_cols].sum()

plt.figure(figsize=(6,6))
plt.pie(
    age_totals,
    labels=["Age 0–5", "Age 5–17", "Age 18+"],
    autopct="%1.1f%%",
    startangle=140
)
plt.title("Aadhaar Enrolment Distribution by Age Group")
plt.tight_layout()
plt.show()

# ======================================================
# 7. LINE CHART: ENROLMENT TREND OVER TIME
# ======================================================

df["date"] = pd.to_datetime(
    df["date"], format="mixed", dayfirst=True, errors="coerce"
)
df = df[df["date"].notna()]

daily_trend = (
    df.groupby("date")["total_enrolments"]
    .sum()
    .reset_index()
)

plt.figure(figsize=(12,5))
plt.plot(daily_trend["date"], daily_trend["total_enrolments"], linewidth=2)
plt.xlabel("Date")
plt.ylabel("Total Enrolments")
plt.title("Aadhaar Enrolment Trend Over Time")
plt.grid(True)
plt.tight_layout()
plt.show()

# ======================================================
# 8. FINAL INSIGHTS (CONSOLE)
# ======================================================

print("\n=== KEY INSIGHTS SUMMARY ===")
print("• Aadhaar enrolments are concentrated in high-population states.")
print("• Adult (18+) category dominates overall enrolment share.")
print("• Time-series shows non-uniform enrolment with visible peaks.")
print("• Trends indicate scope for seasonal and regional planning.")
