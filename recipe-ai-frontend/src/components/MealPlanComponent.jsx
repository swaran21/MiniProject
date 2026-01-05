import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function MealPlanComponent({ user }) {
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getMealPlan = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMealPlan(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/meal-plan/generate?userId=${user.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}), // Backend will fetch user profile
      });

      if (!response.ok) {
        throw new Error("Failed to generate plan");
      }

      const data = await response.json();
      setMealPlan(data);
    } catch (err) {
      console.error("Error:", err);
      setError("Could not generate plan. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  // Helper function for meal type icons
  const getMealIcon = (type) => {
    const icons = {
      'Breakfast': '🌅',
      'Lunch': '🌞',
      'Dinner': '🌙',
      'Snack': '🍪'
    };
    return icons[type] || '🍽️';
  };

  return (
    <div className="component-card">
      <h2>📅 AI Meal Planner</h2>
      <p style={{ color: "#666", marginBottom: "20px" }}>
        Generate a complete day's meal plan based on your profile.
      </p>

      {user && (
        <div style={{ background: "#e3f2fd", padding: "15px", borderRadius: "8px", marginBottom: "20px" }}>
          <strong>Your Profile:</strong> {user.age || "N/A"} yrs, {user.weightKg || "N/A"}kg, Goal: {user.healthGoals || "Balanced"}
        </div>
      )}

      <form onSubmit={getMealPlan}>
        <button type="submit" className="action-button full-width" disabled={loading}>
          {loading ? "Generating..." : "Generate Today's Meal Plan"}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

        {mealPlan && (
          <div className="result-card">
            <h3>🍽️ Your Personalized Meal Plan</h3>
            <div style={{ 
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              padding: "15px",
              borderRadius: "8px",
              color: "white",
              marginBottom: "20px"
            }}>
              <p style={{ margin: "0 0 5px 0", fontSize: "16px" }}>
                <strong>Daily Target:</strong> {mealPlan.totalDailyCalories} kcal
              </p>
              <p style={{ margin: 0, opacity: 0.9, fontSize: "14px" }}>
                Goal: {mealPlan.goal}
              </p>
            </div>

            <h4 style={{ marginBottom: "15px", color: "#333" }}>📋 Your Meals ({mealPlan.meals.length})</h4>
            <div>
              {mealPlan.meals.map((meal, idx) => {
                // Color coding based on meal type (same as diet tracker)
                let borderColor = "#667eea";
                if (meal.type === "Breakfast") borderColor = "#FF9800";
                else if (meal.type === "Lunch") borderColor = "#4CAF50";
                else if (meal.type === "Dinner") borderColor = "#2196F3";
                else if (meal.type === "Snack") borderColor = "#E91E63";

                return (
                  <details 
                    key={idx} 
                    style={{ 
                      marginBottom: "15px",
                      border: "1px solid #e0e0e0",
                      borderLeft: `5px solid ${borderColor}`,
                      borderRadius: "8px",
                      overflow: "hidden",
                      boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
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
                      <span style={{ color: "#333" }}>
                        {getMealIcon(meal.type)} <strong>{meal.type}:</strong> {meal.name || "AI Generated Meal"}
                      </span>
                      <span style={{ 
                        background: borderColor,
                        color: "white",
                        padding: "4px 12px",
                        borderRadius: "20px",
                        fontSize: "13px",
                        marginLeft: "10px",
                        fontWeight: "bold"
                      }}>
                        {meal.calories} kcal
                      </span>
                    </summary>
                  
                  <div style={{ padding: "20px", background: "white" }}>
                    {/* Ingredients Section */}
                    <div style={{ marginBottom: "20px" }}>
                      <h5 style={{ 
                        color: borderColor,  // Use meal-specific color
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
                        {meal.ingredients?.map((ing, i) => (
                          <li key={i} style={{ marginBottom: "5px", color: "#333" }}>{ing}</li>
                        )) || <li style={{ color: "#666" }}>No ingredients available</li>}
                      </ul>
                    </div>

                    {/* Instructions Section */}
                    <div>
                      <h5 style={{ 
                        color: borderColor,  // Use meal-specific color
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
                        {meal.instructions || "No instructions available"}
                      </p>
                    </div>

                    {/* Nutrition Info */}
                    {meal.macros && (
                      <div style={{
                        marginTop: "20px",
                        padding: "12px",
                        background: "#f8f9fa",
                        borderRadius: "6px",
                        fontSize: "13px",
                        color: "#666"
                      }}>
                        <strong>Nutrition:</strong> {meal.macros}
                      </div>
                    )}
                  </div>
                </details>
              );
            })}
            </div>
            <div style={{ 
              marginTop: "20px",
              padding: "15px",
              background: "#e3f2fd",
              borderRadius: "8px",
              fontSize: "14px"
            }}>
              <strong>💡 Tip:</strong> Click on any meal above to see the full recipe with ingredients and cooking instructions!
            </div>
          </div>
        )}
      </div>
    );
  }
  
  export default MealPlanComponent;