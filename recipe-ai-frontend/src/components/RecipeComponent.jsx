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
      {/* Header with toggle button */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h2>🍳 AI Recipe Generator</h2>
        {user && user.id && (
          <button 
            onClick={() => setShowSaved(!showSaved)}
            style={{ 
              padding: "10px 20px", 
              background: showSaved ? "#4CAF50" : "#667eea", 
              color: "white", 
              border: "none", 
              borderRadius: "8px", 
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "bold",
              boxShadow: "0 2px 4px rgba(0,0,0,0.2)"
            }}
          >
            {showSaved ? "➕ Generate New Recipe" : `📚 My Saved Recipes (${savedRecipes.length})`}
          </button>
        )}
      </div>

      {/* Generate New Recipe View */}
      {!showSaved ? (
        <>
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
            <div className="result-card" style={{ marginTop: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                <h3 style={{ margin: 0 }}>{recipe.title}</h3>
                {user && user.id && (
                  <button 
                    onClick={saveRecipe}
                    style={{ 
                      padding: "10px 20px", 
                      background: "#4CAF50", 
                      color: "white", 
                      border: "none", 
                      borderRadius: "6px", 
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: "bold",
                      whiteSpace: "nowrap"
                    }}
                  >
                    💾 Save Recipe
                  </button>
                )}
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
        /* Saved Recipes View */
        <div>
          <div style={{ 
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
            padding: "20px", 
            borderRadius: "10px", 
            color: "white",
            marginBottom: "20px"
          }}>
            <h3 style={{ margin: "0 0 10px 0" }}>📚 Your Saved Recipes</h3>
            <p style={{ margin: 0, opacity: 0.9 }}>
              You have {savedRecipes.length} {savedRecipes.length === 1 ? 'recipe' : 'recipes'} saved
            </p>
          </div>

          {savedRecipes.length === 0 ? (
            <div style={{ 
              textAlign: "center", 
              padding: "40px 20px", 
              background: "#f5f5f5", 
              borderRadius: "10px",
              border: "2px dashed #ccc"
            }}>
              <p style={{ fontSize: "48px", margin: "0 0 10px 0" }}>📭</p>
              <h3>No Saved Recipes Yet</h3>
              <p style={{ color: "#666", marginBottom: "20px" }}>
                Generate some recipes and click the "💾 Save Recipe" button to save your favorites!
              </p>
              <button 
                onClick={() => setShowSaved(false)}
                style={{ 
                  padding: "10px 20px", 
                  background: "#667eea", 
                  color: "white", 
                  border: "none", 
                  borderRadius: "6px", 
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                ➕ Generate Your First Recipe
              </button>
            </div>
          ) : (
            <div>
              {savedRecipes.map((r, idx) => (
                <div 
                  key={idx} 
                  className="result-card" 
                  style={{ 
                    marginBottom: "20px",
                    border: "1px solid #e0e0e0",
                    borderLeft: "4px solid #667eea"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                    <h4 style={{ margin: 0, color: "#333" }}>{r.title}</h4>
                    <button 
                      onClick={() => deleteSavedRecipe(r.savedId)}
                      style={{ 
                        padding: "6px 12px", 
                        background: "#f44336", 
                        color: "white", 
                        border: "none", 
                        borderRadius: "4px", 
                        cursor: "pointer",
                        fontSize: "12px"
                      }}
                    >
                      🗑️ Delete
                    </button>
                  </div>
                  
                  <p style={{ color: "#666", fontSize: "14px", marginBottom: "10px" }}>
                    <strong>{r.calories} cal</strong> • Saved on {new Date(r.savedAt).toLocaleDateString()}
                  </p>
                  
                  <details style={{ marginTop: "10px" }}>
                    <summary style={{ 
                      cursor: "pointer", 
                      padding: "8px", 
                      background: "#f5f5f5", 
                      borderRadius: "4px",
                      fontWeight: "500"
                    }}>
                      👁️ View Full Recipe
                    </summary>
                    <div style={{ marginTop: "15px" }}>
                      <h5 style={{ marginBottom: "10px" }}>Ingredients:</h5>
                      <ul style={{ marginLeft: "20px" }}>
                        {r.ingredients?.map((ing, i) => <li key={i}>{ing}</li>)}
                      </ul>
                      <h5 style={{ marginTop: "15px", marginBottom: "10px" }}>Instructions:</h5>
                      <p style={{ lineHeight: "1.6" }}>{r.instructions}</p>
                    </div>
                  </details>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RecipeComponent;