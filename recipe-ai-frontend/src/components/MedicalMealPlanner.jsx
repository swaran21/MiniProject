import React, { useState } from 'react';

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

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Failed to generate meal plan: ${response.status}`);
      }

      const text = await response.text();
      console.log('Response text:', text);
      
      if (!text) {
        throw new Error('Empty response from server');
      }

      const data = JSON.parse(text);
      setMealPlan(data);
    } catch (err) {
      console.error('Full error:', err);
      setError(`Failed to generate meal plan: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ 
            fontSize: '42px', 
            color: 'white', 
            margin: '0 0 10px 0',
            fontWeight: '700',
            textShadow: '0 2px 10px rgba(0,0,0,0.2)'
          }}>
            🍽️ Medical Meal Planner
          </h1>
          <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.9)', margin: 0 }}>
            Generate personalized meal plans based on your medical conditions
          </p>
        </div>

      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '32px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        marginBottom: '20px'
      }}>
        <h3 style={{ marginTop: 0, color: '#333', fontSize: '24px', marginBottom: '20px' }}>
          Select Your Medical Conditions:
        </h3>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
          <select
            value={newCondition}
            onChange={(e) => setNewCondition(e.target.value)}
            style={{
              flex: 1,
              padding: '10px',
              border: '2px solid #e0e0e0',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          >
            <option value="">-- Select Condition --</option>
            {conditionOptions.map(opt => (
              <option key={opt} value={opt}>
                {opt.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
          <button
            onClick={addCondition}
            disabled={!newCondition}
            style={{
              padding: '10px 20px',
              background: newCondition ? '#667eea' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: newCondition ? 'pointer' : 'not-allowed'
            }}
          >
            Add
          </button>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <strong style={{ color: '#333', fontSize: '16px' }}>Selected Conditions:</strong>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
            {conditions.length === 0 ? (
              <p style={{ color: '#999', fontStyle: 'italic' }}>No conditions selected</p>
            ) : (
              conditions.map(cond => (
                <div key={cond} style={{
                  padding: '6px 12px',
                  background: '#e0f0ff',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  {cond.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  <button
                    onClick={() => removeCondition(cond)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#c00',
                      cursor: 'pointer',
                      fontSize: '16px',
                      padding: 0
                    }}
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '12px', fontWeight: '700', fontSize: '16px', color: '#333' }}>
            Plan Duration: <span style={{ color: '#667eea' }}>{duration} days</span>
          </label>
          <input
            type="range"
            min="7"
            max="90"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            style={{ width: '100%' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666' }}>
            <span>7 days</span>
            <span>30 days</span>
            <span>90 days</span>
          </div>
        </div>

        {error && (
          <div style={{
            padding: '12px',
            background: '#fee',
            color: '#c00',
            borderRadius: '6px',
            marginBottom: '16px'
          }}>
            ⚠️ {error}
          </div>
        )}

        <button
          onClick={generatePlan}
          disabled={loading || conditions.length === 0}
          style={{
            width: '100%',
            padding: '12px',
            background: (loading || conditions.length === 0) ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: (loading || conditions.length === 0) ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '⏳ Generating Plan...' : '✨ Generate Meal Plan'}
        </button>
      </div>

      {mealPlan && (
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '32px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}>
          <h3 style={{ color: '#333', fontSize: '28px', marginTop: 0 }}>
            📅 Your {mealPlan.duration_days}-Day Meal Plan
          </h3>
          <p style={{ whiteSpace: 'pre-wrap', background: '#f9f9f9', padding: '16px', borderRadius: '8px' }}>
            {mealPlan.summary}
          </p>

          <div style={{ marginTop: '24px' }}>
            <h4 style={{ color: '#333', fontSize: '20px' }}>Sample Daily Meals (First 7 Days):</h4>
            {mealPlan.daily_meals?.slice(0, 7).map((day) => (
              <div key={day.day} style={{
                marginBottom: '16px',
                padding: '16px',
                background: '#f5f5f5',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 12px 0' }}>Day {day.day} ({day.date})</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                  <div>
                    <strong>🍳 Breakfast:</strong>
                    <p style={{ margin: '4px 0' }}>{day.breakfast.title}</p>
                    <small>📊 {day.breakfast.health_score}/100 | 🔥 {day.breakfast.calories} cal</small>
                  </div>
                  <div>
                    <strong>🥗 Lunch:</strong>
                    <p style={{ margin: '4px 0' }}>{day.lunch.title}</p>
                    <small>📊 {day.lunch.health_score}/100 | 🔥 {day.lunch.calories} cal</small>
                  </div>
                  <div>
                    <strong>🍛 Dinner:</strong>
                    <p style={{ margin: '4px 0' }}>{day.dinner.title}</p>
                    <small>📊 {day.dinner.health_score}/100 | 🔥 {day.dinner.calories} cal</small>
                  </div>
                </div>
                <p style={{ marginTop: '8px', fontSize: '13px', color: '#666' }}>
                  <strong>Total Daily Calories:</strong> {day.total_calories}
                </p>
              </div>
            ))}
          </div>

          <div style={{
            marginTop: '20px',
            padding: '16px',
            background: '#fff7e0',
            borderRadius: '8px'
          }}>
            <p style={{ margin: 0, fontSize: '13px' }}>
              💡 <strong>Tip:</strong> This plan includes {mealPlan.duration_days} days of meals. 
              Each day has been customized to avoid your restricted foods and include recommended nutritious options.
            </p>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

export default MedicalMealPlanner;
