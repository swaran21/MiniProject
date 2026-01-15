import React, { useState, useEffect } from 'react';
import './RecipeDetailModal.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function RecipeDetailModal({ recipeId, recipeName, mealType, onClose }) {
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecipeDetails();
  }, [recipeId]);

  const fetchRecipeDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/recipes/${recipeId}/details`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recipe: ${response.statusText}`);
      }

      const data = await response.json();
      setRecipe(data);
    } catch (err) {
      console.error("Error fetching recipe details:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="recipe-detail-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="recipe-header">
          <div>
            <span className="meal-type-badge">{mealType}</span>
            <h2>{recipeName}</h2>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading recipe details...</p>
          </div>
        )}

        {error && (
          <div className="error-state">
            <p>❌ {error}</p>
            <p>Could not load recipe details. Please try again.</p>
          </div>
        )}

        {recipe && !loading && (
          <div className="recipe-content">
            {/* Recipe Image */}
            {recipe.imageUrl && (
              <div className="recipe-image-container">
                <img src={recipe.imageUrl} alt={recipe.title} className="recipe-image" />
              </div>
            )}

            {/* Nutrition Summary */}
            <div className="nutrition-summary">
              <div className="nutrition-item">
                <span className="nutrition-label">Calories</span>
                <span className="nutrition-value">{recipe.calories || 'N/A'}</span>
              </div>
              <div className="nutrition-item">
                <span className="nutrition-label">Cuisine</span>
                <span className="nutrition-value">{recipe.cuisineType || 'N/A'}</span>
              </div>
            </div>

            {/* Ingredients */}
            {recipe.ingredients && recipe.ingredients.length > 0 && (
              <div className="recipe-section">
                <h3>🧂 Ingredients</h3>
                <ul className="ingredients-list">
                  {recipe.ingredients.map((ingredient, index) => (
                    <li key={index}>{ingredient}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Instructions */}
            {recipe.instructions && (
              <div className="recipe-section">
                <h3>👨‍🍳 Instructions</h3>
                <div className="instructions-text">
                  {recipe.instructions}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RecipeDetailModal;
