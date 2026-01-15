import React, { useState } from 'react';
import './MedicalMealPlanner.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function MedicalMealPlanner() {
  const [conditions, setConditions] = useState([]);
  const [newCondition, setNewCondition] = useState('');
  const [duration, setDuration] = useState(30);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const conditionOptions = [
    'diabetes_type2',
    'hypertension',
    'high_cholesterol',
    'kidney_disease',
    'pcos',
    'thyroid_hypothyroid',
    'ibs',
    'anemia',
    'gastritis',
    'post_surgery'
  ];

  const addCondition = () => {
    if (newCondition && !conditions.includes(newCondition)) {
      setConditions([...conditions, newCondition]);
      setNewCondition('');
    }
  };

  const removeCondition = (cond) => {
    setConditions(conditions.filter(c => c !== cond));
  };

  const generatePlan = async () => {
    if (conditions.length === 0) {
      setError('Please select at least one medical condition');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/health/generate-meal-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conditions,
          duration_days: duration,
          user_id: 1
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }

      const text = await response.text();
      if (!text) {
        throw new Error('Empty response from server. Please check backend logs.');
      }

      const data = JSON.parse(text);
      if (data.error) {
        throw new Error(data.error);
      }
      
      setMealPlan(data);
    } catch (err) {
      console.error('Meal Plan Generation Error:', err);
      // Backend might be offline or blocked
      if (err.message.includes('Failed to fetch')) {
        setError("Could not connect to server. Is the backend running?");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="medical-meal-planner">
      <div className="mmp-container">
        {/* Header */}
        <div className="mmp-header">
          <h1 className="mmp-title">🍽️ Medical Meal Planner</h1>
          <p className="mmp-subtitle">Generic AI-driven nutrition plans for managing health conditions</p>
        </div>

        {/* Configuration Card */}
        <div className="mmp-card">
          <h3 className="mmp-section-title">Step 1: Select Your Conditions</h3>

          <div className="mmp-controls">
            <select
              className="mmp-select"
              value={newCondition}
              onChange={(e) => setNewCondition(e.target.value)}
            >
              <option value="">-- Select Condition --</option>
              {conditionOptions.map(opt => (
                <option key={opt} value={opt}>
                  {opt.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
            <button 
              className="mmp-btn-add"
              onClick={addCondition}
              disabled={!newCondition}
            >
              Add Condition
            </button>
          </div>

          <div className="mmp-tags-section">
            <label className="mmp-tags-label">Selected Conditions:</label>
            <div className="mmp-tags-container">
              {conditions.length === 0 ? (
                <span className="mmp-empty-tags">None selected. Add a condition above.</span>
              ) : (
                conditions.map(cond => (
                  <div key={cond} className="mmp-tag">
                    {cond.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    <button className="mmp-tag-remove" onClick={() => removeCondition(cond)}>×</button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mmp-slider-container">
            <div className="mmp-slider-label">
              <span>Plan Duration</span>
              <span className="mmp-slider-value">{duration} days</span>
            </div>
            <input
              type="range"
              min="7"
              max="90"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              className="mmp-range"
            />
            <div className="mmp-range-labels">
              <span>7 days</span>
              <span>30 days</span>
              <span>90 days</span>
            </div>
          </div>

          {error && (
            <div className="mmp-error">
              ⚠️ {error}
            </div>
          )}

          <button
            className="mmp-btn-generate"
            onClick={generatePlan}
            disabled={loading || conditions.length === 0}
          >
            {loading ? '⏳ Analyzing Health Data & Generating Plan...' : '✨ Generate Personalized Meal Plan'}
          </button>
        </div>

        {/* Results Card */}
        {mealPlan && (
          <div className="mmp-card">
            <h3 className="mmp-results-header">
              📅 Your {mealPlan.duration_days}-Day Health Plan
            </h3>
            
            <div className="mmp-summary">
              {mealPlan.summary}
            </div>

            <div style={{ marginTop: '20px', marginBottom: '20px', textAlign: 'center' }}>
              <strong style={{ fontSize: '1.1rem', color: '#667eea' }}>
                📅 Showing all {mealPlan.daily_meals?.length} days of your meal plan
              </strong>
            </div>

            <div className="mmp-daily-grid">
              {mealPlan.daily_meals?.map((day) => (
                <div key={day.day} className="mmp-day-card">
                  <h4 className="mmp-day-header">Day {day.day}</h4>
                  
                  <div className="mmp-meal-item">
                    <span className="mmp-meal-label">🍳 Breakfast</span>
                    <p className="mmp-meal-name">{day.breakfast.title}</p>
                    <div className="mmp-meal-stats">
                       {day.breakfast.calories} kcal • Score: {day.breakfast.health_score}
                    </div>
                  </div>

                  <div className="mmp-meal-item">
                    <span className="mmp-meal-label">🥗 Lunch</span>
                    <p className="mmp-meal-name">{day.lunch.title}</p>
                    <div className="mmp-meal-stats">
                       {day.lunch.calories} kcal • Score: {day.lunch.health_score}
                    </div>
                  </div>

                  <div className="mmp-meal-item">
                    <span className="mmp-meal-label">🍛 Dinner</span>
                    <p className="mmp-meal-name">{day.dinner.title}</p>
                    <div className="mmp-meal-stats">
                       {day.dinner.calories} kcal • Score: {day.dinner.health_score}
                    </div>
                  </div>

                  <div className="mmp-day-total">
                    <strong>Total: {day.total_calories} kcal</strong>
                  </div>
                </div>
              ))}
            </div>

            <div className="mmp-tip-box">
              <p>
                💡 <strong>Medical Note:</strong> This plan is automatically generating using AI based on nutritional guidelines for 
                {conditions.join(', ')}. Always verify with your healthcare provider.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MedicalMealPlanner;
