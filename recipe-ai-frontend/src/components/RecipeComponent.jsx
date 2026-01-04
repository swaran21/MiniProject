import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function RecipeComponent({ user }) {
  const [ingredients, setIngredients] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateRecipe = async (e) => {
    e.preventDefault();
    setLoading(true);
    setRecipe(null);
    
    try {
      const params = new URLSearchParams({
        ingredients: ingredients,
        cuisine: cuisine || "any",
      });
      
      // Add userId if user is logged in
      if (user && user.id) {
        params.append("userId", user.id);
      }

      const response = await fetch(`${API_BASE_URL}/api/recipes/generate?${params}`);
      const data = await response.json();
      setRecipe(data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card">
      <h2>🍳 AI Recipe Generator</h2>
      {user && user.dietaryRestrictions && (
        <p style={{ background: "#e3f2fd", padding: "10px", borderRadius: "5px", marginBottom: "15px" }}>
          Recipes will be tailored to your dietary preference: <strong>{user.dietaryRestrictions}</strong>
        </p>
      )}
      <form onSubmit={generateRecipe}>
        <div className="form-group">
          <label>Ingredients (comma separated)</label>
          <input 
            type="text" 
            placeholder="e.g. Chicken, Tomato, Garlic" 
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Cuisine Preference (Optional)</label>
          <input 
            type="text" 
            placeholder="e.g. Italian, Mexican, Indian"
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
          />
        </div>
        <button type="submit" className="action-button full-width" disabled={loading}>
          {loading ? "Generating..." : "Generate Recipe"}
        </button>
      </form>

      {recipe && (
        <div className="result-card">
          <h3>{recipe.title}</h3>
          <div className="recipe-details">
            <span className="tag cuisine">{recipe.cuisineType}</span>
            <span className="tag calories">{recipe.calories} cal</span>
          </div>
          <div className="ingredients-list">
            <strong>Ingredients:</strong>
            <ul>
              {recipe.ingredients.map((ing, idx) => (
                <li key={idx}>{ing}</li>
              ))}
            </ul>
          </div>
          <div className="instructions">
            <strong>Instructions:</strong>
            <p>{recipe.instructions}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecipeComponent;