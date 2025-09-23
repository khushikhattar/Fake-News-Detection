import React, { useState, useEffect } from "react";
import axios from "axios";

const PredictForm = () => {
  const [text, setText] = useState("");
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  // Fetching available models from the backend
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/models/")
      .then((response) => {
        setModels(response.data.models);
        if (response.data.models.length > 0) {
          setSelectedModel(response.data.models[0]);
        }
      })
      .catch((err) => {
        console.error("Error fetching models:", err);
        setError("Failed to fetch models from the backend.");
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text || !selectedModel) {
      setError("Please enter text and select a model.");
      return;
    }

    axios
      .post("http://127.0.0.1:8000/predict/", {
        text: text,
        model: selectedModel,
      })
      .then((response) => {
        setPrediction(response.data);
        setError(null);
      })
      .catch((err) => {
        console.error("Error predicting news:", err);
        setError("Failed to get prediction. Please try again.");
      });
  };

  return (
    <div className="predict-form">
      <h1>Fake News Detection</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <textarea
          rows="5"
          cols="50"
          placeholder="Enter news article here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        ></textarea>
        <br />
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
        <br />
        <button type="submit">Predict</button>
      </form>
      {prediction && (
        <div className="result">
          <h2>Prediction Result</h2>
          <p>
            <strong>Text:</strong> {prediction.text}
          </p>
          <p>
            <strong>Prediction:</strong> {prediction.prediction}
          </p>
          <p>
            <strong>Model Used:</strong> {prediction.model}
          </p>
        </div>
      )}
    </div>
  );
};

export default PredictForm;
