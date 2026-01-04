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
        <div className="result-card" style={{ marginTop: "25px" }}>
          <h3>{mealPlan.goal}</h3>
          <p><strong>Total Daily Calories:</strong> {mealPlan.totalDailyCalories} kcal</p>
          <p>{mealPlan.suggestion}</p>

          <div style={{ marginTop: "20px" }}>
            <h4>Your Meals:</h4>
            {mealPlan.meals.map((meal, idx) => (
              <div key={idx} style={{ 
                background: "#f8f9fa", 
                padding: "15px", 
                borderRadius: "8px", 
                marginBottom: "10px",
                borderLeft: "4px solid #667eea"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h5 style={{ margin: 0 }}>{meal.name} ({meal.type})</h5>
                  <span style={{ fontWeight: "bold", color: "#667eea" }}>{meal.calories} kcal</span>
                </div>
                <p style={{ margin: "5px 0 0 0", fontSize: "0.9rem", color: "#666" }}>{meal.macros}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default MealPlanComponent;