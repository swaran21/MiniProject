import React, { useState } from "react";

const API_BASE_URL = "http://localhost:8080";

function DietTrackerComponent({ user }) {
  const [foodItem, setFoodItem] = useState("");
  const [mealType, setMealType] = useState("Lunch");
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getAdvice = async (e) => {
    e.preventDefault();
    setLoading(true);
    setRecommendation(null);
    setError("");

    const payload = {
      foodItem: foodItem,
      mealType: mealType,
      userProfile: null
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/diet/recommend?userId=${user.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Failed to get advice");
      const data = await response.json();
      console.log("API Response:", data);
      setRecommendation(data);
    } catch (err) {
      console.error(err);
      setError("System Error. Ensure Java Backend (8080) & Python ML (5000) are running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card">
      <h2>🍽️ Smart Diet Tracker</h2>
      <p style={{ color: "#666", marginBottom: "20px" }}>
        Log your meals and get AI-powered recommendations for the rest of your day.
      </p>

      <div style={{ background: "#e3f2fd", padding: "15px", borderRadius: "8px", marginBottom: "20px" }}>
        <strong>Your Profile:</strong> {user.age || "N/A"} yrs, {user.weightKg || "N/A"}kg, Goal: {user.healthGoals || "Balanced"}
      </div>

      <form onSubmit={getAdvice}>
        <h4 style={{ margin: "0 0 10px 0", color: "#444" }}>Log Your Meal</h4>
        <div className="form-group">
          <label>What did you just eat?</label>
          <input 
            type="text" 
            value={foodItem} 
            onChange={(e) => setFoodItem(e.target.value)} 
            placeholder="e.g., Cheese Pizza" 
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
          {loading ? "Analyzing..." : "Get Smart Recommendation"}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

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
                  cardColor = "#FFF3E0";
                  borderColor = "#FF9800";
                  icon = "🌅";
                } else if (meal.type.includes("Lunch")) {
                  cardColor = "#E8F5E9";
                  borderColor = "#4CAF50";
                  icon = "🥗";
                } else if (meal.type.includes("Dinner")) {
                  cardColor = "#E3F2FD";
                  borderColor = "#2196F3";
                  icon = "🌙";
                } else {
                  cardColor = "#FCE4EC";
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
             <div style={{ background: "#fff", borderLeft: "5px solid #607D8B", padding: "15px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
              <div style={{ display: "flex", alignItems: "center", marginBottom: "5px" }}>
                 <h5 style={{ margin: 0, fontSize: "1.1rem", color: "#333" }}>💡 Recommendation</h5>
              </div>
              <p style={{ margin: 0, color: "#555" }}>{recommendation.nextMealSuggestion}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DietTrackerComponent;
