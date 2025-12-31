import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function RecipeComponent() {
  const [ingredients, setIngredients] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateRecipe = async (e) => {
    e.preventDefault();
    setLoading(true);
    setRecipe(null);
    
    try {
      // Build query string
      const params = new URLSearchParams({
        ingredients: ingredients,
        cuisine: cuisine || "any",
      });

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
            placeholder="e.g. Italian, Mexican" 
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
          />
        </div>
        <button type="submit" className="action-button full-width" disabled={loading}>
          {loading ? "Cooking up magic..." : "Generate Recipe"}
        </button>
      </form>

      {recipe && (
        <div className="recipe-card">
          <img src={recipe.imageUrl} alt="Dish" className="recipe-image"/>
          <h3>{recipe.title}</h3>
          <div className="tags">
            <span className="tag cuisine">{recipe.cuisineType}</span>
            <span className="tag calories">{recipe.calories} kcal</span>
          </div>
          
          <h4>Ingredients:</h4>
          <ul>
            {recipe.ingredients.map((ing, index) => (
              <li key={index}>{ing}</li>
            ))}
          </ul>

          <h4>Instructions:</h4>
          <p className="instructions">{recipe.instructions}</p>
        </div>
      )}
    </div>
  );
}

export default RecipeComponent;