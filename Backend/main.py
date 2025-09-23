from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

# Defining the folder containing models and vectorizer
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Loading the TF-IDF vectorizer
vectorizer_path = os.path.join(CURRENT_DIR, "tfidf_vectorizer.joblib")
if not os.path.exists(vectorizer_path):
    raise FileNotFoundError("TF-IDF vectorizer not found in the current directory.")
vectorizer = joblib.load(vectorizer_path)

# Dynamically loading all models from the folder
models = {}
for filename in os.listdir(CURRENT_DIR):
    if filename.endswith(".joblib") and filename != "tfidf_vectorizer.joblib":
        model_name = filename.replace(".joblib", "")  # Remove file extension
        models[model_name] = joblib.load(os.path.join(CURRENT_DIR, filename))

# Creating FastAPI app
app = FastAPI()

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

class NewsRequest(BaseModel):
    text: str
    model: str

@app.get("/")
def home():
    return {"message": "Welcome to the Fake News Detection API!"}

@app.get("/models/")
def get_models():
    return {"models": list(models.keys())}

@app.post("/predict/")
def predict_news(data: NewsRequest):
    if data.model not in models:
        raise HTTPException(status_code=400, detail="Invalid model name.")

    # Preprocessing input text
    def wordopt(text):
        import re
        import string
        text = text.lower()
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r"https?://\S+|www\.\S+", '', text)
        text = re.sub(r'<.*?>+', '', text)
        text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub(r'\n', '', text)
        text = re.sub(r'\w*\d\w*', '', text)
        return text

    processed_text = wordopt(data.text)
    vectorized_text = vectorizer.transform([processed_text])

    model = models[data.model]
    prediction = model.predict(vectorized_text)[0]

    result = "Fake News" if prediction == 0 else "Not A Fake News"
    return {"text": data.text, "prediction": result, "model": data.model}
