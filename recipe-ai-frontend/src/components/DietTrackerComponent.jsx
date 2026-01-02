import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function DietTrackerComponent({ userProfile }) {
  // 1. Profile Data State (Pre-filled from persistent profile)
  const [profileData, setProfileData] = useState(userProfile || {
    weightKg: "",
    heightCm: "",
    age: "",
    gender: "M",
    activityLevel: "Moderate",
    healthGoals: "Balanced",
    dietaryRestrictions: "None"
  });

  // 2. Meal Entry State
  const [foodItem, setFoodItem] = useState("");
  const [mealType, setMealType] = useState("Lunch");
  
  // 3. UI States
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleProfileChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };

  const getAdvice = async (e) => {
    e.preventDefault();
    setLoading(true);
    setRecommendation(null);
    setError("");

    // Prepare the payload exactly as the Java Backend expects
    const payload = {
      foodItem: foodItem,
      mealType: mealType,
      userProfile: {
        weightKg: parseFloat(profileData.weightKg) || 70, // Default if empty
        heightCm: parseFloat(profileData.heightCm) || 170,
        age: parseInt(profileData.age) || 25,
        gender: profileData.gender,
        activityLevel: profileData.activityLevel,
        healthGoals: profileData.healthGoals,
        dietaryRestrictions: profileData.dietaryRestrictions
      }
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/diet/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to get advice from server.");
      }

      const data = await response.json();
      console.log("API Response:", data); // Debugging
      setRecommendation(data);
    } catch (err) {
      console.error("Error:", err);
      setError("Could not connect to the Smart Diet System.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card">
      <h2>🍽️ Smart Diet Tracker</h2>
      <p style={{ color: "#666", marginBottom: "20px" }}>
        Tell us what you ate, and we'll calculate your next move.
      </p>

      <form onSubmit={getAdvice}>
        {/* Context Section: User Profile (Simplified for this view) */}
        <div style={{ background: "#f8f9fa", padding: "15px", borderRadius: "8px", marginBottom: "20px" }}>
          <h4 style={{ margin: "0 0 10px 0", color: "#444" }}>Step 1: Your Context</h4>
          <div className="grid-form">
            <div className="form-group">
              <label>Weight (kg)</label>
              <input 
                type="number" 
                name="weightKg" 
                value={profileData.weightKg} 
                onChange={handleProfileChange} 
                placeholder="e.g., 75" 
                required 
              />
            </div>
            <div className="form-group">
              <label>Current Goal</label>
              <select name="healthGoals" value={profileData.healthGoals} onChange={handleProfileChange}>
                <option value="Balanced">Balanced Diet</option>
                <option value="Lose Weight">Lose Weight</option>
                <option value="Gain Muscle">Gain Muscle</option>
              </select>
            </div>
          </div>
        </div>

        {/* Input Section: The Meal */}
        <h4 style={{ margin: "0 0 10px 0", color: "#444" }}>Step 2: The Meal</h4>
        <div className="form-group">
          <label>What did you just eat?</label>
          <input 
            type="text" 
            value={foodItem} 
            onChange={(e) => setFoodItem(e.target.value)} 
            placeholder="e.g., Cheese Pizza, Grilled Chicken Salad" 
            required 
            style={{ padding: "12px", fontSize: "1.1rem" }}
          />
        </div>

        <div className="form-group">
          <label>Meal Type</label>
          <select value={mealType} onChange={(e) => setMealType(e.target.value)}>
            <option value="Breakfast">Breakfast</option>
            <option value="Lunch">Lunch</option>
            <option value="Dinner">Dinner</option>
            <option value="Snack">Snack</option>
          </select>
        </div>

        <button type="submit" className="action-button full-width" disabled={loading}>
          {loading ? "Analyzing Meal..." : "Get Smart Recommendation"}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

{/* Results Section */}
      {recommendation && (
        <div className="result-card" style={{ display: "block", marginTop: "25px", borderLeft: "5px solid #4CAF50" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
            <span className="tag calories" style={{ fontSize: "1rem" }}>
              Consumed: <strong>{recommendation.caloriesConsumedEstimate} kcal</strong>
            </span>
            <span className="tag cuisine" style={{ fontSize: "1rem" }}>
              Remaining: <strong>{recommendation.caloriesRemaining} kcal</strong>
            </span>
          </div>

          <div style={{ marginBottom: "15px" }}>
            <h4 style={{ color: "#d32f2f", margin: "0 0 5px 0" }}>Analysis:</h4>
            <p style={{ margin: 0 }}>{recommendation.nutritionalAnalysis}</p>
          </div>

          <h4 style={{ color: "#2E7D32", margin: "0 0 15px 0" }}>Your Full Day Plan:</h4>
          
          {recommendation.dayPlan && recommendation.dayPlan.length > 0 ? (
            <div style={{ display: "grid", gap: "15px" }}>
              {recommendation.dayPlan.map((meal, idx) => {
                let cardColor = "#fff";
                let borderColor = "#ccc";
                let icon = "🍽️";

                if (meal.type.includes("Breakfast")) {
                  cardColor = "#FFF3E0"; // Warm Orange
                  borderColor = "#FF9800";
                  icon = "🌅";
                } else if (meal.type.includes("Lunch")) {
                  cardColor = "#E8F5E9"; // Fresh Green
                  borderColor = "#4CAF50";
                  icon = "🥗";
                } else if (meal.type.includes("Dinner")) {
                  cardColor = "#E3F2FD"; // Calm Blue
                  borderColor = "#2196F3";
                  icon = "🌙";
                } else {
                  cardColor = "#FCE4EC"; // Pink Snack
                  borderColor = "#E91E63";
                  icon = "🍎";
                }

                return (
                  <div key={idx} style={{ 
                    background: cardColor, 
                    borderLeft: `5px solid ${borderColor}`, 
                    padding: "15px", 
                    borderRadius: "8px",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "5px" }}>
                      <h5 style={{ margin: 0, fontSize: "1.1rem", color: "#333" }}>{icon} {meal.type}</h5>
                      <span style={{ fontWeight: "bold", color: borderColor }}>{meal.recipe.calories} kcal</span>
                    </div>
                    <h4 style={{ margin: "5px 0", color: "#444" }}>{meal.recipe.title}</h4>
                    <p style={{ fontSize: "0.9rem", color: "#666", marginBottom: "5px" }}>
                      <em>{meal.recipe.ingredients.slice(0, 4).join(", ")}...</em>
                    </p>
                    <small style={{ color: "#777", display: "block", marginTop: "5px" }}>
                      💡 {meal.suggestionReason}
                    </small>
                  </div>
                );
              })}
            </div>
          ) : (
             <div style={{ background: "#e8f5e9", padding: "10px", borderRadius: "5px" }}>
              <p style={{ margin: 0, fontWeight: "500" }}>{recommendation.nextMealSuggestion}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DietTrackerComponent;