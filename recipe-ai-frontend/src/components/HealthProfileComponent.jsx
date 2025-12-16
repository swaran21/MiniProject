import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function HealthProfileComponent() {
  const [formData, setFormData] = useState({
    weightKg: "",
    heightCm: "",
    age: "",
    gender: "M",
    activityLevel: "Moderate",
    healthGoals: "Maintain Weight"
  });
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const analyzeHealth = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/api/health/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="component-card">
      <h2>📊 Your Health Profile</h2>
      <form onSubmit={analyzeHealth} className="grid-form">
        <div className="form-group">
          <label>Weight (kg)</label>
          <input type="number" name="weightKg" onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Height (cm)</label>
          <input type="number" name="heightCm" onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Age</label>
          <input type="number" name="age" onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Gender</label>
          <select name="gender" onChange={handleChange}>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>
        <button type="submit" className="action-button full-width">Analyze My Health</button>
      </form>

      {result && (
        <div className="result-card">
          <div className="stat-box">
            <h3>BMI</h3>
            <p className="highlight">{result.bmi}</p>
            <span className="badge">{result.bmiCategory}</span>
          </div>
          <div className="stat-box">
            <h3>Daily Calories</h3>
            <p className="highlight">{result.dailyCalorieNeeds} kcal</p>
            <span>to maintain weight</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default HealthProfileComponent;