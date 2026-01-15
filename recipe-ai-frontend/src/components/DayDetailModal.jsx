import React, { useState } from 'react';
import './DayDetailModal.css';
import RecipeDetailModal from './RecipeDetailModal';

function DayDetailModal({ day, onClose }) {
  const [selectedMeal, setSelectedMeal] = useState(null);

  const handleMealClick = (meal, mealType) => {
    setSelectedMeal({ ...meal, mealType });
  };

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="day-detail-modal" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="modal-header">
            <div>
              <h2>Day {day.day} Meals</h2>
              <p className="modal-date">{day.date}</p>
            </div>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>

          {/* Meals Grid */}
          <div className="meals-grid">
            {/* Breakfast */}
            <div 
              className="meal-card clickable" 
              onClick={() => handleMealClick(day.breakfast, 'Breakfast')}
            >
              <div className="meal-card-header">
                <span className="meal-icon">🍳</span>
                <h3>Breakfast</h3>
              </div>
              <p className="meal-title">{day.breakfast.title}</p>
              <div className="meal-stats">
                <span>{day.breakfast.calories} kcal</span>
                <span>❤️ {day.breakfast.healthScore || 100}</span>
              </div>
            </div>

            {/* Lunch */}
            <div 
              className="meal-card clickable" 
              onClick={() => handleMealClick(day.lunch, 'Lunch')}
            >
              <div className="meal-card-header">
                <span className="meal-icon">🥗</span>
                <h3>Lunch</h3>
              </div>
              <p className="meal-title">{day.lunch.title}</p>
              <div className="meal-stats">
                <span>{day.lunch.calories} kcal</span>
                <span>❤️ {day.lunch.healthScore || 100}</span>
              </div>
            </div>

            {/* Dinner */}
            <div 
              className="meal-card clickable" 
              onClick={() => handleMealClick(day.dinner, 'Dinner')}
            >
              <div className="meal-card-header">
                <span className="meal-icon">🍛</span>
                <h3>Dinner</h3>
              </div>
              <p className="meal-title">{day.dinner.title}</p>
              <div className="meal-stats">
                <span>{day.dinner.calories} kcal</span>
                <span>❤️ {day.dinner.healthScore || 100}</span>
              </div>
            </div>
          </div>

          {/* Daily Summary */}
          <div className="day-summary">
            <h3>Daily Total</h3>
            <div className="summary-stats">
              <div className="stat-item">
                <span className="stat-label">Calories</span>
                <span className="stat-value">{day.total_calories} kcal</span>
              </div>
              {day.totalMacrosBreakdown && (
                <>
                  <div className="stat-item">
                    <span className="stat-label">Protein</span>
                    <span className="stat-value">{day.totalMacrosBreakdown.protein}g</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Carbs</span>
                    <span className="stat-value">{day.totalMacrosBreakdown.carbs}g</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Fats</span>
                    <span className="stat-value">{day.totalMacrosBreakdown.fats}g</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recipe Detail Modal (nested) */}
      {selectedMeal && (
        <RecipeDetailModal
          recipeId={selectedMeal.recipeId}
          recipeName={selectedMeal.title}
          mealType={selectedMeal.mealType}
          onClose={() => setSelectedMeal(null)}
        />
      )}
    </>
  );
}

export default DayDetailModal;
