import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function RecipeRating({ recipeId, user }) {
  const [rating, setRating] = useState(null);
  const [stats, setStats] = useState({ likes: 0, dislikes: 0, total_ratings: 0 });
  const [loading, setLoading] = useState(false);

  // Fetch current rating stats on mount
  React.useEffect(() => {
    console.log("RecipeRating mounted with recipeId:", recipeId); // Debug
    if (recipeId) {
      fetchRating();
    }
  }, [recipeId]);

  const fetchRating = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/recipes/${recipeId}/rating`);
      if (response.ok) {
        const data = await response.json();
        setStats({
          likes: data.likes || 0,
          dislikes: data.dislikes || 0,
          total_ratings: data.total_ratings || 0
        });
      }
    } catch (error) {
      console.error('Failed to fetch rating:', error);
    }
  };

  const handleRating = async (ratingValue) => {
    setLoading(true);
    
    const userId = user?.id || 'anonymous';
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/recipes/${recipeId}/rate?rating=${ratingValue}&userId=${userId}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        const data = await response.json();
        setRating(ratingValue);
        setStats({
          likes: data.likes || 0,
          dislikes: data.dislikes || 0,
          total_ratings: data.total_ratings || 0
        });
      }
    } catch (error) {
      console.error('Failed to rate recipe:', error);
    } finally {
      setLoading(false);
    }
  };

  const percentage = stats.total_ratings > 0 
    ? Math.round((stats.likes / stats.total_ratings) * 100) 
    : 50;

  // Don't show rating for ML-generated recipes (no ID)
  if (!recipeId) {
    return null;
  }

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '15px 20px',
      borderRadius: '10px',
      marginTop: '15px',
      color: 'white'
    }}>
      <div style={{ marginBottom: '10px', fontSize: '14px', fontWeight: '500' }}>
        Rate this recipe:
      </div>
      
      <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
        <button
          onClick={() => handleRating(1)}
          disabled={loading}
          style={{
            padding: '12px 24px',
            background: rating === 1 ? '#4CAF50' : 'rgba(255, 255, 255, 0.2)',
            border: '2px solid white',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            fontWeight: 'bold',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.3s ease',
            opacity: loading ? 0.5 : 1
          }}
        >
          👍 {stats.likes}
        </button>

        <button
          onClick={() => handleRating(-1)}
          disabled={loading}
          style={{
            padding: '12px 24px',
            background: rating === -1 ? '#f44336' : 'rgba(255, 255, 255, 0.2)',
            border: '2px solid white',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            fontWeight: 'bold',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.3s ease',
            opacity: loading ? 0.5 : 1
          }}
        >
          👎 {stats.dislikes}
        </button>

        <div style={{ flex: 1, marginLeft: '10px' }}>
          <div style={{ fontSize: '12px', marginBottom: '5px', opacity: 0.9 }}>
            {percentage}% liked ({stats.total_ratings} ratings)
          </div>
          <div style={{
            height: '6px',
            background: 'rgba(255, 255, 255, 0.3)',
            borderRadius: '3px',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${percentage}%`,
              background: '#4CAF50',
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecipeRating;
