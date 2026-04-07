import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Insurance Premium Predictor", page_icon="💰")

st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below:")

# ------------------ Input Fields ------------------
age = st.number_input("Age", min_value=1, max_value=119, value=30)

weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)

height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)

income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)

smoker = st.selectbox("Are you a smoker?", [True, False])

city = st.text_input("City", value="Mumbai")

occupation = st.selectbox(
    "Occupation",
    [
        "retired",
        "freelancer",
        "student",
        "government_job",
        "business_owner",
        "unemployed",
        "private_job",
    ],
)

# ------------------ Prediction Button ------------------
if st.button("Predict Premium Category"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation,
    }

    with st.spinner("Predicting..."):
        try:
            response = requests.post(API_URL, json=input_data, timeout=5)
            response.raise_for_status()

            result = response.json()

            st.success(
                f"Predicted Insurance Premium Category: **{result['predicted_category']}**"
            )

            st.write("🔍 **Confidence:**", result["confidence"])

            st.write("📊 **Class Probabilities:**")
            st.json(result["class_probabilities"])

        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the FastAPI server. Is it running?")

        except requests.exceptions.Timeout:
            st.error("⏳ Request timed out. Please try again.")

        except requests.exceptions.HTTPError as e:
            st.error("❌ API returned an error")
            st.exception(e)

        except KeyError:
            st.error("❌ Unexpected API response format")
            st.json(result)
