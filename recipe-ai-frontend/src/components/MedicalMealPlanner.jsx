import React, { useState, useEffect } from 'react';
import './MedicalMealPlanner.css';
import { saveMealPlan, getActiveMealPlan, deleteMealPlan } from '../services/mealPlanService';
import MealPlanSuccessModal from './MealPlanSuccessModal';
import WeekCalendar from './WeekCalendar';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function MedicalMealPlanner() {
  const [conditions, setConditions] = useState([]);
  const [newCondition, setNewCondition] = useState('');
  const [duration, setDuration] = useState(30);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savedPlan, setSavedPlan] = useState(null);
  const [viewMode, setViewMode] = useState('generate'); // 'generate', 'saved', 'calendar'
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const userId = 1; // TODO: Get from auth context

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
      // Auto-save REMOVED - User must click Save button
      
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

  // Load saved plan on component mount
  useEffect(() => {
    loadSavedPlan();
  }, []);

  const loadSavedPlan = async () => {
    try {
      const plan = await getActiveMealPlan(userId);
      if (plan) {
        setSavedPlan(plan);
        console.log('✅ Loaded saved meal plan from database');
      }
    } catch (err) {
      console.error('Error loading saved plan:', err);
    }
  };

  const handleSavePlan = async () => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      await saveMealPlan(mealPlan, userId);
      console.log('✅ Meal plan saved manually');
      await loadSavedPlan(); // Reload to update state
      setShowSuccessModal(true); // Show success popup!
    } catch (err) {
      console.error('Failed to save plan:', err);
      setError('Failed to save meal plan: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePlan = async () => {
    if (!savedPlan || !confirm('Are you sure you want to delete this meal plan? This will also remove all tracked progress.')) {
      return;
    }

    try {
      await deleteMealPlan(savedPlan.planId);
      setSavedPlan(null);
      setMealPlan(null);
      setViewMode('generate');
      console.log('✅ Meal plan deleted');
    } catch (err) {
      console.error('Error deleting plan:', err);
      setError('Failed to delete meal plan');
    }
  };

  const viewSavedPlan = () => {
    if (savedPlan) {
      prepareDisplayPlan(savedPlan);
      setViewMode('saved');
    }
  };

  const prepareDisplayPlan = (sourcePlan) => {
      // Convert savedPlan (Java DTO format) to display format
      const displayPlan = {
        plan_id: sourcePlan.planId,
        duration_days: sourcePlan.durationDays,
        conditions: sourcePlan.conditions,
        summary: sourcePlan.summary,
        daily_meals: sourcePlan.dailyMeals.map(day => ({
          day: day.day,
          date: day.date,
          total_calories: day.totalCalories,
          breakfast: day.breakfast,
          lunch: day.lunch,
          dinner: day.dinner,
          snacks: day.snacks || []
        }))
      };
      setMealPlan(displayPlan);
  };

  const handleOpenCalendar = () => {
    setShowSuccessModal(false);
    if (!mealPlan && savedPlan) {
        prepareDisplayPlan(savedPlan);
    }
    setViewMode('calendar');
  };

  return (
    <div className="medical-meal-planner">
      <div className="mmp-container">
        
        {/* SUCCESS MODAL POPUP */}
        {showSuccessModal && (
          <MealPlanSuccessModal 
            onOpenCalendar={handleOpenCalendar}
            onClose={() => setShowSuccessModal(false)}
          />
        )}

        {/* CALENDAR VIEW MODE */}
        {viewMode === 'calendar' && mealPlan && (
            <WeekCalendar 
                plan={mealPlan} 
                onClose={() => setViewMode('saved')}
                onDelete={handleDeletePlan}
            />
        )}

        {/* Header */}
        {viewMode !== 'calendar' && (
        <div className="mmp-header">
          <h1 className="mmp-title">🍽️ Medical Meal Planner</h1>
          <p className="mmp-subtitle">AI-driven nutrition plans for managing health conditions</p>
          
          {/* Saved Plan Actions */}
          {savedPlan && viewMode !== 'saved' && (
            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
              <button 
                className="mmp-button-secondary" 
                onClick={viewSavedPlan}
                style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
              >
                📋 View Saved Plan ({savedPlan.durationDays} days)
              </button>
              
              <button 
                className="mmp-button-primary" 
                onClick={() => { prepareDisplayPlan(savedPlan); setViewMode('calendar'); }}
                style={{ fontSize: '0.9rem', padding: '0.5rem 1rem', background: '#4facfe', color: 'white' }}
              >
                📅 Calendar View
              </button>
            </div>
          )}
        </div>
        )}

        {/* Configuration Card */}
        {viewMode === 'generate' && !mealPlan && !loading && (
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
        )}

        {/* Results Card */}
        {mealPlan && viewMode !== 'calendar' && (
          <div className="mmp-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 className="mmp-results-header" style={{ margin: 0 }}>
                📅 Your {mealPlan.duration_days}-Day Health Plan
              </h3>
              
              <div className="mmp-actions">
                {viewMode === 'generate' && !savedPlan ? (
                  <button 
                    onClick={handleSavePlan}
                    className="mmp-btn-save"
                    style={{ 
                      backgroundColor: '#28a745', 
                      color: 'white', 
                      padding: '0.5rem 1rem', 
                      borderRadius: '5px', 
                      border: 'none', 
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}
                    disabled={loading}
                  >
                   💾 {loading ? 'Saving...' : 'Save Plan'}
                  </button>
                ) : (
                  viewMode === 'generate' && (
                    <button 
                        className="mmp-button-danger" 
                        onClick={handleDeletePlan}
                        style={{ fontSize: '0.9rem', padding: '0.5rem 1rem', background: '#dc3545', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer' }}
                    >
                        🗑️ Delete Plan
                    </button>
                  )
                )}
                
                {viewMode === 'saved' && (
                   <div style={{display: 'flex', gap: '10px'}}>
                        <button 
                            onClick={() => setViewMode('calendar')} 
                            className="mmp-button-primary"
                            style={{ padding: '0.5rem 1rem', background: '#4facfe', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                        >
                            📅 Calendar
                        </button>
                       <button 
                         onClick={() => { setMealPlan(null); setViewMode('generate'); }} 
                         style={{ padding: '0.5rem', cursor: 'pointer', background: 'transparent', border: '1px solid #ccc', borderRadius: '5px', color: '#ccc' }}
                       >
                         ✖ Close
                       </button>
                   </div>
                )}
              </div>
            </div>
            
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

                  {/* SNACKS - These are included in the total! */}
                  {day.snacks && day.snacks.length > 0 && (
                    <div className="mmp-meal-item" style={{ borderTop: '1px dashed #e0e0e0', paddingTop: '10px', marginTop: '10px' }}>
                      <span className="mmp-meal-label">🍿 Snacks</span>
                      {day.snacks.map((snack, idx) => (
                        <div key={idx} style={{ marginTop: '5px', fontSize: '0.9rem' }}>
                          <p className="mmp-meal-name" style={{ fontSize: '0.95rem' }}>{snack.title}</p>
                          <div className="mmp-meal-stats" style={{ fontSize: '0.85rem' }}>
                            {snack.calories} kcal • Score: {snack.health_score}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

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
