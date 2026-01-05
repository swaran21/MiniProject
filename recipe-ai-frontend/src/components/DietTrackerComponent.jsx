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
                let borderColor = "#ccc";
                let icon = "🍽️";

                if (meal.type.includes("Breakfast")) {
                  borderColor = "#FF9800";
                  icon = "🌅";
                } else if (meal.type.includes("Lunch")) {
                  borderColor = "#4CAF50";
                  icon = "🥗";
                } else if (meal.type.includes("Dinner")) {
                  borderColor = "#2196F3";
                  icon = "🌙";
                } else {
                  borderColor = "#E91E63";
                  icon = "🍎";
                }

                return (
                  <details 
                    key={idx} 
                    style={{ 
                      border: "1px solid #e0e0e0",
                      borderLeft: `5px solid ${borderColor}`,
                      borderRadius: "8px",
                      overflow: "hidden"
                    }}
                  >
                    <summary style={{ 
                      padding: "15px",
                      cursor: "pointer",
                      background: "#f8f9fa",
                      fontWeight: "500",
                      fontSize: "16px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      userSelect: "none",
                      color: "#333"
                    }}>
                      <span>
                        {icon} <strong>{meal.type}:</strong> {meal.recipe.title}
                      </span>
                      <span style={{ 
                        background: borderColor,
                        color: "white",
                        padding: "4px 12px",
                        borderRadius: "20px",
                        fontSize: "13px",
                        marginLeft: "10px"
                      }}>
                        {meal.recipe.calories} kcal
                      </span>
                    </summary>
                    
                    <div style={{ padding: "20px", background: "white" }}>
                      {/* Ingredients Section */}
                      <div style={{ marginBottom: "20px" }}>
                        <h5 style={{ 
                          color: borderColor, 
                          marginBottom: "10px",
                          fontSize: "14px",
                          textTransform: "uppercase",
                          letterSpacing: "0.5px"
                        }}>
                          🥘 Ingredients
                        </h5>
                        <ul style={{ 
                          margin: 0,
                          paddingLeft: "20px",
                          lineHeight: "1.8",
                          color: "#333"
                        }}>
                          {meal.recipe.ingredients?.map((ing, i) => (
                            <li key={i} style={{ marginBottom: "5px", color: "#333" }}>{ing}</li>
                          )) || <li style={{ color: "#666" }}>No ingredients available</li>}
                        </ul>
                      </div>

                      {/* Instructions Section */}
                      <div>
                        <h5 style={{ 
                          color: borderColor, 
                          marginBottom: "10px",
                          fontSize: "14px",
                          textTransform: "uppercase",
                          letterSpacing: "0.5px"
                        }}>
                          📝 Instructions
                        </h5>
                        <p style={{ 
                          margin: 0,
                          lineHeight: "1.8",
                          color: "#333",
                          whiteSpace: "pre-wrap"
                        }}>
                          {meal.recipe.instructions || "No instructions available"}
                        </p>
                      </div>

                      {/* Suggestion Reason */}
                      <div style={{
                        marginTop: "20px",
                        padding: "12px",
                        background: "#f8f9fa",
                        borderRadius: "6px",
                        fontSize: "13px",
                        color: "#666"
                      }}>
                        <strong>💡 Why this meal?</strong> {meal.suggestionReason}
                      </div>
                    </div>
                  </details>
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
