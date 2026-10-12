import math
import os

import requests
import streamlit as st


DEFAULT_API_URL = "https://mansik-santulan-score.onrender.com"

st.set_page_config(
    page_title="Mental Health Signal",
    page_icon="🌿",
    layout="centered",
)

st.title("Mental Health Signal")
st.write(
    "Estimate a mental health score from your daily habits. "
    "This is for informational purposes only and is not a clinical assessment."
)

api_url = os.getenv("PREDICTION_API_URL", DEFAULT_API_URL).rstrip("/")

with st.form("prediction_form"):
    st.subheader("Profile")
    age = st.number_input("Age", min_value=10, max_value=100, value=21, step=1)
    gender = st.selectbox("Gender", ["Male", "Female"])
    country = st.text_input("Country", placeholder="e.g. India")

    st.subheader("Academic and digital habits")
    academic_level = st.selectbox(
        "Academic level", ["High School", "Undergraduate", "Graduate"]
    )
    most_used_platform = st.selectbox(
        "Most-used platform",
        [
            "Facebook",
            "Instagram",
            "Snapchat",
            "Twitter",
            "YouTube",
            "TikTok",
            "LinkedIn",
            "LINE",
            "KakaoTalk",
            "VKontakte",
            "WhatsApp",
            "WeChat",
        ],
    )
    purpose_of_use = st.selectbox(
        "Primary purpose", ["Networking", "Education", "Entertainment", "News"]
    )
    avg_daily_usage_hours = st.number_input(
        "Average daily screen time (hours)",
        min_value=0.0,
        max_value=24.0,
        value=4.0,
        step=0.1,
    )
    daily_unlocks = st.number_input(
        "Daily phone unlocks", min_value=0, value=60, step=1
    )

    st.subheader("Lifestyle and stress")
    study_hours = st.number_input(
        "Study hours per day", min_value=0.0, max_value=24.0, value=3.0, step=0.1
    )
    physical_activity_hours = st.number_input(
        "Physical activity per day (hours)",
        min_value=0.0,
        max_value=24.0,
        value=1.0,
        step=0.1,
    )
    sleep_hours_per_night = st.number_input(
        "Sleep per night (hours)",
        min_value=0.0,
        max_value=24.0,
        value=8.0,
        step=0.1,
    )
    stress_level = st.selectbox(
        "Perceived stress level", ["Low", "Medium", "High", "Very High"]
    )

    submitted = st.form_submit_button("Read my signal", type="primary")

if submitted:
    if not country.strip():
        st.error("Enter your country to continue.")
    else:
        payload = {
            "age": age,
            "gender": gender,
            "country": country.strip(),
            "academic_level": academic_level,
            "most_used_platform": most_used_platform,
            "purpose_of_use": purpose_of_use,
            "avg_daily_usage_hours": avg_daily_usage_hours,
            "daily_unlocks": daily_unlocks,
            "study_hours": study_hours,
            "physical_activity_hours": physical_activity_hours,
            "sleep_hours_per_night": sleep_hours_per_night,
            "stress_level": stress_level,
        }

        try:
            response = requests.post(
                f"{api_url}/predict",
                json=payload,
                timeout=90,
            )
        except requests.RequestException as exc:
            st.error(f"Could not reach the prediction service: {exc}")
        else:
            if response.status_code == 422:
                try:
                    details = response.json().get("detail", [])
                except requests.exceptions.JSONDecodeError:
                    st.error("The prediction service rejected the inputs.")
                else:
                    if isinstance(details, list):
                        for detail in details:
                            if isinstance(detail, dict):
                                location = detail.get("loc", [])
                                field = location[-1] if location else "Input"
                                st.error(f"{field}: {detail.get('msg', 'Invalid value.')}")
                            else:
                                st.error(str(detail))
                    else:
                        st.error(str(details))
            elif not response.ok:
                st.error(
                    f"The prediction service returned HTTP {response.status_code}."
                )
            else:
                try:
                    result = response.json()
                except requests.exceptions.JSONDecodeError:
                    st.error("The prediction service returned invalid JSON.")
                else:
                    score = (
                        result.get("predicted_mental_health_score")
                        if isinstance(result, dict)
                        else None
                    )
                    if type(score) not in (int, float) or not math.isfinite(score):
                        st.error("The prediction service returned an invalid score.")
                    else:
                        score = float(score)
                        st.metric("Predicted score", f"{score:.2f} / 10")
                        st.progress(max(0.0, min(1.0, score / 10)))
                        if score < 4:
                            st.info(
                                "Your responses suggest elevated strain right now. "
                                "Small shifts in sleep or screen time may help."
                            )
                        elif score < 7:
                            st.info(
                                "Your rhythm looks fairly steady, with some room "
                                "to recover and reset."
                            )
                        else:
                            st.info(
                                "Your habits point to a well-supported baseline. "
                                "Keep taking care of yourself."
                            )

st.caption(
    "This tool is informational only, not a diagnosis. If you are struggling, "
    "please talk to someone you trust or a qualified professional."
)
