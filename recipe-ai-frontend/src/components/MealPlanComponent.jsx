import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function MealPlanComponent({ userProfile }) {
  // Pre-fill form with global user profile
  const [formData, setFormData] = useState(userProfile || {
    weightKg: "",
    heightCm: "",
    age: "",
    gender: "M",
    activityLevel: "Moderate",
    healthGoals: "Balanced", // Default goal
    dietaryRestrictions: ""
  });

  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle text field changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const getMealPlan = async (e) => {
    e.preventDefault(); // Prevent page reload
    setLoading(true);
    setError("");
    setMealPlan(null);

    try {
      // Now we send the ACTUAL user inputs to the backend
      const response = await fetch(`${API_BASE_URL}/api/meal-plan/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to generate plan. Please check your connection.");
      }

      const data = await response.json();
      setMealPlan(data);
    } catch (err) {
      console.error("Error:", err);
      setError("Could not generate plan. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card">
      <h2>📅 Personalized Meal Planner</h2>
      
      {/* The Input Form matching Backend Expectations */}
      <form onSubmit={getMealPlan} className="grid-form">
        <div className="form-group">
          <label>Weight (kg):</label>
          <input 
            type="number" 
            name="weightKg" 
            value={formData.weightKg} 
            onChange={handleChange} 
            required 
            placeholder="e.g. 70"
          />
        </div>

        <div className="form-group">
          <label>Height (cm):</label>
          <input 
            type="number" 
            name="heightCm" 
            value={formData.heightCm} 
            onChange={handleChange} 
            required 
            placeholder="e.g. 175"
          />
        </div>

        <div className="form-group">
          <label>Age:</label>
          <input 
            type="number" 
            name="age" 
            value={formData.age} 
            onChange={handleChange} 
            required 
            placeholder="e.g. 25"
          />
        </div>

        <div className="form-group">
          <label>Gender:</label>
          <select name="gender" value={formData.gender} onChange={handleChange}>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>

        <div className="form-group">
          <label>Activity Level:</label>
          <select name="activityLevel" value={formData.activityLevel} onChange={handleChange}>
            <option value="Sedentary">Sedentary (Little exercise)</option>
            <option value="Moderate">Moderate (Exercise 1-3 times/week)</option>
            <option value="Active">Active (Exercise 4-5 times/week)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Goal:</label>
          <select name="healthGoals" value={formData.healthGoals} onChange={handleChange}>
            <option value="Balanced">Balanced Diet</option>
            <option value="Lose Weight">Lose Weight</option>
            <option value="Gain Muscle">Gain Muscle</option>
          </select>
        </div>

        <button 
          type="submit" 
          className="action-button full-width"
          disabled={loading}
        >
          {loading ? "Generating Plan..." : "Create My Plan"}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {/* The Results Display */}
      {mealPlan && (
        <div className="plan-results">
          <div className="plan-header">
            <h3>Daily Target: {mealPlan.totalDailyCalories} kcal</h3>
            <p className="suggestion">💡 {mealPlan.suggestion}</p>
          </div>
          
          <div className="meals-list">
            {mealPlan.meals.map((meal, index) => (
              <div key={index} className="meal-item">
                <div className="meal-type-badge">{meal.type}</div>
                <div className="meal-content">
                  <h4>{meal.name}</h4>
                  <div className="meal-stats">
                    <span>🔥 {meal.calories} kcal</span>
                    <span>🥗 {meal.macros}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default MealPlanComponent;