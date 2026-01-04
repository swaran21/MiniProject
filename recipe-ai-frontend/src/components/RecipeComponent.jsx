import React, { useState, useEffect } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function RecipeComponent({ user }) {
  const [ingredients, setIngredients] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [savedRecipes, setSavedRecipes] = useState([]);
  const [showSaved, setShowSaved] = useState(false);

  // Load saved recipes on mount
  useEffect(() => {
    if (user && user.id) {
      fetchSavedRecipes();
    }
  }, [user]);

  const fetchSavedRecipes = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/recipes/saved?userId=${user.id}`);
      const data = await response.json();
      setSavedRecipes(data);
    } catch (error) {
      console.error("Failed to fetch saved recipes:", error);
    }
  };

  const generateRecipe = async (e) => {
    e.preventDefault();
    setLoading(true);
    setRecipe(null);
    
    try {
      const params = new URLSearchParams({
        ingredients: ingredients,
        cuisine: cuisine || "any",
      });
      
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

  const saveRecipe = async () => {
    if (!user || !user.id) {
      alert("Please log in to save recipes");
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/recipes/save?userId=${user.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(recipe)
      });
      
      const data = await response.json();
      if (response.ok) {
        alert("Recipe saved!");
        fetchSavedRecipes();
      } else {
        alert("Failed: " + (data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error saving:", error);
      alert("Failed to save recipe");
    }
  };

  const deleteSavedRecipe = async (savedId) => {
    if (!confirm("Delete this recipe?")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/recipes/saved/${savedId}?userId=${user.id}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        alert("Deleted!");
        fetchSavedRecipes();
      }
    } catch (error) {
      console.error("Error deleting:", error);
    }
  };

  return (
    <div className="component-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h2>🍳 AI Recipe Generator</h2>
        <button 
          onClick={() => setShowSaved(!showSaved)}
          style={{ padding: "8px 15px", background: "#667eea", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}
        >
          {showSaved ? "Generate New" : `💾 Saved (${savedRecipes.length})`}
        </button>
      </div>

      {user && user.dietaryRestrictions && !showSaved && (
        <p style={{ background: "#e3f2fd", padding: "10px", borderRadius: "5px", marginBottom: "15px" }}>
          Recipes will be tailored to your dietary preference: <strong>{user.dietaryRestrictions}</strong>
        </p>
      )}

      {!showSaved ? (
        <>
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
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3>{recipe.title}</h3>
                <button 
                  onClick={saveRecipe}
                  style={{ padding: "8px 15px", background: "#4CAF50", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}
                >
                  💾 Save
                </button>
              </div>
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
        </>
      ) : (
        <div>
          <h3>Your Saved Recipes ({savedRecipes.length})</h3>
          {savedRecipes.length === 0 ? (
            <p>No saved recipes yet. Generate and save some!</p>
          ) : (
            savedRecipes.map((r, idx) => (
              <div key={idx} className="result-card" style={{ marginTop: "15px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <h4>{r.title}</h4>
                  <button 
                    onClick={() => deleteSavedRecipe(r.savedId)}
                    style={{ padding: "5px 10px", background: "#f44336", color: "white", border: "none", borderRadius: "3px", cursor: "pointer" }}
                  >
                    🗑️
                  </button>
                </div>
                <p>{r.calories} cal | Saved: {new Date(r.savedAt).toLocaleDateString()}</p>
                <details>
                  <summary style={{ cursor: "pointer", marginTop: "10px" }}>View Recipe</summary>
                  <h5>Ingredients:</h5>
                  <ul>
                    {r.ingredients?.map((ing, i) => <li key={i}>{ing}</li>)}
                  </ul>
                  <h5>Instructions:</h5>
                  <p>{r.instructions}</p>
                </details>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default RecipeComponent;