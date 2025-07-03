import streamlit as st
import os
import json
import requests
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import load_model
from googletrans import Translator
from auth_simple import register_user, login_user
import gdown

st.set_page_config(page_title="Plant Health App", layout="wide")

# Cache model to optimize performance
# @st.cache_resource
# def load_plant_model():
#     model_path = os.path.join(os.path.dirname(__file__), "plant_disease_prediction_model.h5")
#     return load_model(model_path, compile=False)


@st.cache_resource
def load_plant_model():
    model_path = os.path.join(os.path.dirname(__file__), "plant_disease_prediction_model.h5")
    if not os.path.exists(model_path):
        url = "https://drive.google.com/uc?id=1SgexqL2DYL5ZmGuaNEMvr-28c3Zo-aN3"
        gdown.download(url, model_path, quiet=False)
    return load_model(model_path, compile=False)

# Load static JSON data once
@st.cache_resource
def load_json(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name), "r") as file:
        return json.load(file)

working_dir = os.path.dirname(os.path.abspath(__file__))


#--------------------------------login start ---------------------------------------
# Session variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""


if not st.session_state.logged_in:
    choice = st.sidebar.selectbox("Login/Register", ["Login", "Register"])

    if choice == "Login":
        st.title("🌾 Agro Vision App")
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome back, {username}!")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    elif choice == "Register":
        st.title("🌾 Agro Vision App")
        st.subheader("Register")
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(username, password):
                st.success("Registered successfully! You can now log in.")
            else:
                st.error("Username already exists or registration error.")

else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # Show actual app after login
            
    # Initialize Model & Data
    model = load_plant_model()
    class_indices = load_json("class_indices.json")
    recommendations = load_json("recommendations.json")
    market_data = load_json("market.json")
    fertilizer_stores = load_json("maharashtra_fertilizer_stores.json")
    crop_npk_data = load_json("crop_npk.json")


    # API Configuration
    OPENWEATHER_API_KEY = "e904ee2b79326aba2a44970e6ddce3d1"
    WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

    # Language Selection
    translator = Translator()
    LANG_DICT = {
        "English": {
            "Home": "Home",
            "Disease Detection": "Disease Detection",
            "Market Analysis": "Market Analysis",
            "Weather Analysis": "Weather Analysis",
            "Nearby Stores": "Nearby Stores",
            "Crop Prediction": "Crop Prediction"
        },
        "मराठी": {
            "Home": "मुख्यपृष्ठ",
            "Disease Detection": "रोग शोध",
            "Market Analysis": "बाजार विश्लेषण",
            "Weather Analysis": "हवामान विश्लेषण",
            "Nearby Stores": "नजीकची खते दुकाने",
            "Crop Prediction": "पिक अंदाज"
        }
    }

    st.sidebar.image("logo.jpg", width=100)  # Add logo
    language = st.sidebar.radio("Select Language / भाषा निवडा", ["English", "मराठी"])
   
    def t(text):
        if language == "मराठी":
            translated_text = LANG_DICT[language].get(text, translator.translate(text, dest="mr").text)
            translated_text = translated_text.replace("अॅप", "अ‍ॅप").replace("प्लांट", "वनस्पती").replace("हेल्थ", "आरोग्य")  # Fix incorrect translation
            return translated_text
        return text

   

    #  Sidebar Styling with CSS
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #2E3B55; /* Dark Blue Sidebar */
            padding-top: 20px;
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #FFFFFF;
            text-align: center;
            margin-bottom: 20px;
        }
        .sidebar-button {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 5px 0;
            text-align: center;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background-color: #4CAF50; /* Green buttons */
            border-radius: 8px;
            border: none;
            cursor: pointer;
        }
        .sidebar-button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Utility Functions
    def get_weather(city):
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        try:
            response = requests.get(WEATHER_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def load_and_preprocess_image(image, target_size=(224, 224)):
        img = image.resize(target_size)
        img_array = np.array(img) / 255.0
        return np.expand_dims(img_array, axis=0)

    def predict_image_class(model, image):
        preprocessed_img = load_and_preprocess_image(image)
        predictions = model.predict(preprocessed_img)
        return class_indices.get(str(np.argmax(predictions, axis=1)[0]), "Unknown")

    # UI Components
    def navbar():
        st.markdown(f"<nav style='background:#008000;padding:10px;text-align:center;color:white;'>"
                    f"<h1>{t('Agro Vision App')}</h1></nav>", unsafe_allow_html=True)

    def footer():
        st.markdown(f"<footer style='background:#222;padding:10px;text-align:center;color:white;'>"
                    f"&copy; 2025 {t('Agro Vision App. All Rights Reserved.')}</footer>", unsafe_allow_html=True)

    # Pages
    def home():
        navbar()
        st.header(t("Welcome to Plant Health App 🌿"))
        st.write(t("This app helps in plant disease detection, market analysis for crops, and weather updates."))
        # Add home page content
        st.markdown(f"<h2 style='color:#008000;'>{t('What can you do with this app?')}</h2>", unsafe_allow_html=True)
        st.write(t("1. **Disease Detection**: Upload a leaf photo to identify the disease and get treatment advice."))
        st.write(t("2. **Market Analysis**: Check crop prices and make smart buying or selling decisions."))
        st.write(t("3. **Weather Updates**: Stay up-to-date with the latest weather forecasts, and plan your farming activities accordingly."))
        st.write(t("4. **Nearby Stores**: Find fertilizer stores near your location, and purchase the necessary supplies for your crops."))
        st.write(t("5. **Crop Prediction**: Get personalized crop recommendations based on your soil type, climate, and other factors."))
        # Call to action
        st.markdown(f"<h3 style='color:#008000;'>{t('Get started now!')}</h3>", unsafe_allow_html=True)
        st.write(t("Explore the different features of this app, and start improving your farming practices today!"))
        footer()

    def disease_detection():
        # navbar()
        st.title(t('🌿 Plant Disease Detection'))
        uploaded_image = st.file_uploader(t("📤 Upload an image..."), type=["jpg", "jpeg", "png"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image.resize((150, 150)), caption=t("Uploaded Image"))
            if st.button(t('🔍 Classify')):
                with st.spinner(t("Processing...")):
                    prediction = predict_image_class(model, image)
                    st.success(f'✅ {t("Prediction")}: {t(prediction)}')
                    if prediction in recommendations:
                        for key, value in recommendations[prediction].items():
                            st.write(f"{t(key)}: {t(value)}")
        footer()


    def market_analysis():
        # navbar()
        st.title(t("📊 Market Analysis"))

        selected_crop = st.selectbox(t("Select a Crop:"), list(market_data["crops"].keys()))

        if selected_crop:
            crop_prices = market_data["crops"][selected_crop]
            min_price, max_price = crop_prices["min_price"], crop_prices["max_price"]

            st.success(f'{t("Current market price range for")} {t(selected_crop)}: ₹{min_price} - ₹{max_price}')

            # Plot diagonal line from min to max price
            fig, ax = plt.subplots(figsize=(8, 3))  # Adjusted figure size
            ax.plot([0, 1], [min_price, max_price], marker='o', color='black', linestyle='-', linewidth=3)

            # Set Min/Max labels on X-axis
            ax.set_xticks([0, 1])
            ax.set_xticklabels([t("Min"), t("Max")])  
            ax.set_ylabel(t("Price (₹)"))
            ax.set_title(t(f"Market Price Trend for {selected_crop}"))
            ax.grid(axis='y', linestyle='--', alpha=0.6)

            st.pyplot(fig, use_container_width=False)  # Prevent full-screen width

        footer()


    def weather_analysis():
        # navbar()
        st.title(t("🌦 Weather Analysis"))
        
        city = st.text_input(t("Enter city name:"))
        
        if city and st.button(t("Get Weather")):
            with st.spinner(t("Fetching data...")):
                weather_data = get_weather(city)
            
            if weather_data:
                temp = weather_data['main']['temp']
                humidity = weather_data['main']['humidity']
                wind_speed = weather_data['wind']['speed']
                description = t(weather_data['weather'][0]['description'].capitalize())

                # Define Colors Based on Temperature
                temp_color = "#FF5733" if temp > 30 else "#3498DB"
                
                st.success(f"{t('Weather in')} {city}")

                # Layout using Columns
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"### 🌡 *{t('Temperature')}*")
                    st.markdown(f"<h2 style='color:{temp_color};'>{temp}°C</h2>", unsafe_allow_html=True)

                with col2:
                    st.markdown(f"### 💧 *{t('Humidity')}*")
                    st.markdown(f"<h2 style='color:#1ABC9C;'>{humidity}%</h2>", unsafe_allow_html=True)

                with col3:
                    st.markdown(f"### 💨 *{t('Wind Speed')}*")
                    st.markdown(f"<h2 style='color:#F39C12;'>{wind_speed} m/s</h2>", unsafe_allow_html=True)

                # Weather Condition Box
                st.markdown(
                    f"<div style='background:#2C3E60;padding:10px;border-radius:10px;color:white;text-align:center;'>"
                    f"<h3>☁ {t('Weather Condition')}</h3>"
                    f"<h4>{description}</h4></div> <br>",
                    unsafe_allow_html=True,
                )

            else:
                st.error(t("City not found or API error."))

        footer()



    def nearby_stores():
        # navbar()
        st.title(t("🛒 Nearby Fertilizer Stores"))
        stores_path = os.path.join(working_dir, "maharashtra_fertilizer_stores.json")
        with open(stores_path, "r") as file:
            store_data = json.load(file)
        selected_city = st.selectbox(t("🌍 Select City:"), list(store_data.keys()))
        if st.button(t("🔍 Search Stores")):
            st.subheader(f"{t('Stores in')} {selected_city}:")
            for store in store_data[selected_city]:
                st.write(f"{store['name']} - {store['address']}")
            st.map(pd.DataFrame(store_data[selected_city]))
        footer()

    def crop_prediction():
        # navbar()
        st.title(t("🌾 Crop Prediction"))

        N = st.number_input(t("Enter Nitrogen (N) value"), min_value=0, max_value=300)
        P = st.number_input(t("Enter Phosphorus (P) value"), min_value=0, max_value=300)
        K = st.number_input(t("Enter Potassium (K) value"), min_value=0, max_value=300)

        if st.button(t("🔍 Predict Best Crops")):
            matching_crops = [
                crop for crop, values in crop_npk_data.items()
                if values["N"][0] <= N <= values["N"][1] and
                values["P"][0] <= P <= values["P"][1] and
                values["K"][0] <= K <= values["K"][1]
            ]

            if matching_crops:
                st.success(f"{t('Best Crops for given NPK values')}: 🌾 {', '.join(map(t, matching_crops))}")
            else:
                st.warning(t("No exact match found. Consider adjusting NPK values."))

        footer()

    # Sidebar Navigation
    page = st.sidebar.radio(t("Navigate"), list(LANG_DICT[language].values()))



    if page == t("Home"):
        home()
    elif page == t("Disease Detection"):
        disease_detection()
    elif page == t("Market Analysis"):
        market_analysis()
    elif page == t("Weather Analysis"):
        weather_analysis()
    elif page == t("Nearby Stores"):
        nearby_stores()
    elif page == t("Crop Prediction"):
        crop_prediction()             

    

    #------------------ ---------------login end-------------------------------------------
