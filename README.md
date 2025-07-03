

---

```markdown
# 🌿 Agro Vision - Plant Disease Detection App

Agro Vision is a smart agriculture-focused web app built using **Streamlit** and **Deep Learning**. It helps farmers identify plant diseases using leaf images and offers crop insights, weather updates, and nearby fertilizer store information — all in **English and Marathi**.

---

## 🚀 Features

- 🌱 **Plant Disease Detection** using a pre-trained deep learning model
- 🌍 **Bilingual Support** – English and मराठी
- 🛒 **Nearby Fertilizer Store Locator** (based on Maharashtra data)
- 🌤 **Live Weather Updates** using OpenWeather API
- 🌾 **NPK-based Crop Recommendation**
- 📊 **Crop Market Price Analysis**
- 🔐 **User Authentication** – Register/Login System



## 🧠 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend/Model**: TensorFlow (CNN)
- **Authentication**: Custom login/register (no external DB)
- **APIs**:
  - OpenWeather API
  - Google Drive (via gdown)
- **Language Translation**: Google Translate API

---

## 📁 Project Structure

```

├── app.py                       # Main Streamlit app
├── auth\_simple.py              # Auth logic (register/login)
├── class\_indices.json          # Label mappings
├── crop\_npk.json               # NPK ranges for crops
├── market.json                 # Market price data
├── recommendations.json        # Treatment advice
├── maharashtra\_fertilizer\_stores.json
├── requirements.txt
├── .gitignore
└── README.md

````

---

## 🔧 Setup Instructions

1. **Clone this repo**:
   ```bash
   git clone https://github.com/sarthakghuge18/Agro-Vision.git
   cd Agro-Vision
````

2. **Create virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate    # On Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Download the `.h5` model** (Google Drive):

   ```bash
   pip install gdown
   gdown https://drive.google.com/uc?id=1SgexqL2DYL5ZmGuaNEMvr-28c3Zo-aN3
   ```

5. **Run the app**:

   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployed App

🔗 [Live Demo on Streamlit Cloud](https://agro-vision.streamlit.app)

---

## 🙌 Acknowledgements

* Streamlit for the web framework
* TensorFlow for model training
* OpenWeatherMap API for weather
* Google Translate API for language support


---

## 📫 Contact

**Sarthak Ghuge**
🔗 [LinkedIn](https://www.linkedin.com/in/sarthakghuge18)

---

