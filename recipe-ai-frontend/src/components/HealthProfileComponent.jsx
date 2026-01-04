import React, { useState, useEffect } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function HealthProfileComponent({ user, onUpdateProfile }) {
  const [formData, setFormData] = useState({
    weightKg: "",
    heightCm: "",
    age: "",
    gender: "M",
    activityLevel: "Moderate",
    healthGoals: "Balanced"
  });
  const [result, setResult] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  // Load user data on mount
  useEffect(() => {
    if (user) {
      setFormData({
        weightKg: user.weightKg || "",
        heightCm: user.heightCm || "",
        age: user.age || "",
        gender: user.gender || "M",
        activityLevel: user.activityLevel || "Moderate",
        healthGoals: user.healthGoals || "Balanced"
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const saveProfile = async () => {
    if (onUpdateProfile) {
      onUpdateProfile(formData);
    }
    
    // Also update in backend
    try {
      await fetch(`${API_BASE_URL}/api/auth/profile/${user.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      setIsEditing(false);
    } catch (error) {
      console.error("Error saving profile:", error);
    }
  };

  const analyzeHealth = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${API_BASE_URL}/api/health/analyze?userId=${user.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      setResult({ error: "Could not analyze. Please ensure backend is running." });
    }
  };

  return (
    <div className="component-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h2>📊 Your Health Profile</h2>
        {!isEditing ? (
          <button 
            onClick={() => setIsEditing(true)}
            style={{ padding: "8px 15px", background: "#667eea", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}
          >
            Edit Profile
          </button>
        ) : (
          <button 
            onClick={saveProfile}
            style={{ padding: "8px 15px", background: "#4CAF50", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}
          >
            Save Changes
          </button>
        )}
      </div>

      <form onSubmit={analyzeHealth} className="grid-form">
        <div className="form-group">
          <label>Weight (kg)</label>
          <input 
            type="number" 
            name="weightKg" 
            value={formData.weightKg}
            onChange={handleChange} 
            disabled={!isEditing}
            required 
          />
        </div>
        <div className="form-group">
          <label>Height (cm)</label>
          <input 
            type="number" 
            name="heightCm" 
            value={formData.heightCm}
            onChange={handleChange} 
            disabled={!isEditing}
            required 
          />
        </div>
        <div className="form-group">
          <label>Age</label>
          <input 
            type="number" 
            name="age" 
            value={formData.age}
            onChange={handleChange} 
            disabled={!isEditing}
            required 
          />
        </div>
        <div className="form-group">
          <label>Gender</label>
          <select 
            name="gender" 
            value={formData.gender}
            onChange={handleChange}
            disabled={!isEditing}
          >
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>
        <div className="form-group">
          <label>Activity Level</label>
          <select 
            name="activityLevel" 
            value={formData.activityLevel}
            onChange={handleChange}
            disabled={!isEditing}
          >
            <option value="Sedentary">Sedentary</option>
            <option value="Moderate">Moderate</option>
            <option value="Active">Active</option>
          </select>
        </div>
        <div className="form-group">
          <label>Health Goal</label>
          <select 
            name="healthGoals" 
            value={formData.healthGoals}
            onChange={handleChange}
            disabled={!isEditing}
          >
            <option value="Balanced">Balanced Diet</option>
            <option value="Lose Weight">Lose Weight</option>
            <option value="Gain Muscle">Gain Muscle</option>
          </select>
        </div>
        
        <button type="submit" className="action-button full-width" style={{ gridColumn: "1 / -1" }}>
          Analyze My Health
        </button>
      </form>

      {result && !result.error && (
        <div className="result-card" style={{ marginTop: "25px" }}>
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
      
      {result && result.error && (
        <p className="error-message">{result.error}</p>
      )}
    </div>
  );
}

export default HealthProfileComponent;