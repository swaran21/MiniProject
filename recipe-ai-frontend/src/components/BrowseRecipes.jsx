import React, { useState } from 'react';
import RecipeRating from './RecipeRating';
import apiClient from '../utils/apiClient';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function BrowseRecipes() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchRecipes = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setSelectedRecipe(null);
    setError(null);
    
    try {
      const response = await apiClient.get(`/api/recipes/search`, {
        params: {
          query: searchQuery,
          limit: 20
        }
      });
      
      const data = response.data;
      console.log('Search results:', data); // Debug
      setResults(data);
      
      if (data.length === 0) {
        setError(`No recipes found for "${searchQuery}". Try "curry", "pasta", or "chicken".`);
      }
    } catch (error) {
      console.error('Search failed:', error);
      setError('Search failed. Make sure the servers are running.');
    } finally {
      setLoading(false);
    }
  };

  const loadRecipeDetails = async (recipeId) => {
    try {
      const response = await apiClient.get(`/api/recipes/${recipeId}/details`);
      const data = response.data;
      console.log('Recipe details:', data); // Debug
      setSelectedRecipe(data);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error('Failed to load recipe:', error);
      setError('Failed to load recipe details.');
    }
  };

  return (
    <div className="component-card">
      <h2>📚 Browse Recipes</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Search through 15,000+ recipes by name
      </p>

      {/* Search Bar */}
      <form onSubmit={searchRecipes} style={{ marginBottom: '30px' }}>
        <div className="form-group">
          <input
            type="text"
            placeholder="Search recipe name (e.g., 'chicken curry', 'chocolate cake')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              border: '2px solid #ddd',
              borderRadius: '8px'
            }}
          />
        </div>
        <button 
          type="submit" 
          className="action-button full-width" 
          disabled={loading || !searchQuery.trim()}
        >
          {loading ? 'Searching...' : '🔍 Search Recipes'}
        </button>
      </form>

      {/* Selected Recipe Detail */}
      {selectedRecipe && (
        <div className="result-card" style={{ marginBottom: '30px', borderLeft: '4px solid #4CAF50' }}>
          <button
            onClick={() => setSelectedRecipe(null)}
            style={{
              float: 'right',
              background: '#666',
              color: 'white',
              border: 'none',
              padding: '6px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            ← Back to Results
          </button>
          
          <h3>{selectedRecipe.title}</h3>
          <div className="recipe-details">
            <span className="tag cuisine">{selectedRecipe.cuisine}</span>
          </div>

          <div className="ingredients-list">
            <strong>Ingredients:</strong>
            <ul>
              {selectedRecipe.ingredients.map((ing, idx) => (
                <li key={idx}>{ing}</li>
              ))}
            </ul>
          </div>

          <div className="instructions">
            <strong>Instructions:</strong>
            <p>{selectedRecipe.instructions}</p>
          </div>

          {/* Rating Component */}
          <RecipeRating recipeId={selectedRecipe.id} user={user} />
        </div>
      )}

      {/* Search Results */}
      {!selectedRecipe && results.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '15px' }}>
            Found {results.length} recipes
          </h3>
          
          <div style={{ display: 'grid', gap: '10px' }}>
            {results.map((recipe) => {
              const percentage = recipe.total_ratings > 0
                ? Math.round((recipe.likes / recipe.total_ratings) * 100)
                : 50;

              return (
                <div
                  key={recipe.id}
                  onClick={() => loadRecipeDetails(recipe.id)}
                  style={{
                    padding: '15px',
                    background: 'white',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f5f5f5'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '0 0 5px 0', color: '#333' }}>
                        {recipe.title}
                      </h4>
                      <div style={{ fontSize: '14px', color: '#666' }}>
                        {recipe.cuisine} • {recipe.total_ratings} ratings
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '14px' }}>
                        👍 {recipe.likes} | 👎 {recipe.dislikes}
                      </span>
                      <div style={{
                        background: `linear-gradient(90deg, #4CAF50 ${percentage}%, #ddd ${percentage}%)`,
                        width: '60px',
                        height: '8px',
                        borderRadius: '4px'
                      }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div style={{
          padding: '20px',
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '8px',
          color: '#856404',
          marginTop: '20px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* No Results */}
      {!loading && !selectedRecipe && results.length === 0 && searchQuery && !error && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <p>No recipes found for "{searchQuery}"</p>
          <p style={{ fontSize: '14px' }}>Try different keywords like "pasta", "chicken", or "dessert"</p>
        </div>
      )}
    </div>
  );
}

export default BrowseRecipes;
