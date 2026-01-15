import React, { useState, useEffect } from 'react';
import './WeekCalendar.css';
import { toggleDayCompletion } from '../services/mealPlanService';
import DayDetailModal from './DayDetailModal';

function WeekCalendar({ plan, onClose, onDelete }) {
  const [currentWeek, setCurrentWeek] = useState(0); // 0-indexed week offset
  const [weekDays, setWeekDays] = useState([]);
  const [completedDays, setCompletedDays] = useState({}); // { dayId: boolean }
  const [selectedDay, setSelectedDay] = useState(null); // For day detail modal

  // Total weeks
  const totalWeeks = Math.ceil(plan.duration_days / 7);

  // Initialize completed state from plan data
  useEffect(() => {
    const initialCompleted = {};
    plan.daily_meals.forEach(day => {
        if (day.isCompleted) {
            initialCompleted[day.dayId] = true;
        }
    });
    setCompletedDays(initialCompleted);
  }, [plan]);

  useEffect(() => {
    // Slice meals for the current week
    const startIndex = currentWeek * 7;
    const endIndex = startIndex + 7;
    const days = plan.daily_meals.slice(startIndex, endIndex);
    setWeekDays(days);
  }, [currentWeek, plan]);

  const handleToggle = async (dayId) => {
      // Optimistic update
      const isCompleted = !completedDays[dayId];
      setCompletedDays(prev => ({ ...prev, [dayId]: isCompleted }));

      try {
          await toggleDayCompletion(dayId);
          console.log(`Day ${dayId} toggled to ${isCompleted}`);
      } catch (err) {
          console.error("Failed to toggle day", err);
          // Revert on error
          setCompletedDays(prev => ({ ...prev, [dayId]: !isCompleted }));
      }
  };


  const nextWeek = () => {
    if (currentWeek < totalWeeks - 1) {
      setCurrentWeek(prev => prev + 1);
    }
  };

  const prevWeek = () => {
    if (currentWeek > 0) {
      setCurrentWeek(prev => prev - 1);
    }
  };

  const isToday = (dateString) => {
    const today = new Date().toISOString().split('T')[0];
    return dateString === today;
  };

  return (
    <div className="week-calendar">
      {/* Calendar Header */}
      <div className="calendar-header">
        <div className="calendar-title">
          <h2>📅 Weekly Schedule</h2>
          <div className="calendar-stats">
            Plan Duration: {plan.duration_days} Days • Total Weeks: {totalWeeks}
          </div>
        </div>

        <div className="actions-right">
             <button 
                className="mmp-button-danger" 
                onClick={onDelete}
                style={{
                    marginRight: '0.5rem', 
                    padding: '0.5rem 1rem', 
                    fontSize: '0.9rem',
                    background: '#dc3545', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '8px', 
                    cursor: 'pointer'
                }}
             >
                🗑️ Delete Plan
             </button>
             <button 
                className="mmp-button-secondary" 
                onClick={onClose} 
                style={{
                    marginRight: '1rem',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px'
                }}
             >
                Close
             </button>
            <div className="week-nav">
              <button 
                className="nav-btn" 
                onClick={prevWeek} 
                disabled={currentWeek === 0}
              >
                ◀
              </button>
              <span className="current-week">Week {currentWeek + 1}</span>
              <button 
                className="nav-btn" 
                onClick={nextWeek} 
                disabled={currentWeek === totalWeeks - 1}
              >
                ▶
              </button>
            </div>
        </div>
      </div>

      {/* Days Grid */}
      <div className="days-grid">
        {weekDays.map((day) => {
          const isCompleted = completedDays[day.dayId];
          return (
          <div 
            key={day.day} 
            className={`cal-day-card ${isToday(day.date) ? 'today' : ''} ${isCompleted ? 'completed' : ''}`}
            onClick={() => setSelectedDay(day)}
            style={{ cursor: 'pointer' }}
          >
            <div className="day-header">
              <div style={{display:'flex', alignItems:'center', gap:'10px'}}>
                  <input 
                    type="checkbox" 
                    className="completion-checkbox"
                    checked={!!isCompleted}
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent card click
                      handleToggle(day.dayId);
                    }}
                  />
                  <div>
                    <span className="day-number">Day {day.day}</span>
                    <div className="day-date" style={{fontSize: '0.8rem'}}>{day.date || `-`}</div>
                  </div>
              </div>
              {isCompleted && <span style={{color: '#4caf50', fontWeight: 'bold'}}>✅ Done</span>}
            </div>

            <div className="cal-meals">
              <div className="cal-meal-row">
                <span className="meal-icon">🍳</span>
                <span className="meal-title" title={day.breakfast.title}>
                  {day.breakfast.title}
                </span>
              </div>
              <div className="cal-meal-row">
                <span className="meal-icon">🥗</span>
                <span className="meal-title" title={day.lunch.title}>
                  {day.lunch.title}
                </span>
              </div>
              <div className="cal-meal-row">
                <span className="meal-icon">🍛</span>
                <span className="meal-title" title={day.dinner.title}>
                  {day.dinner.title}
                </span>
              </div>
              
              <div style={{ marginTop: '1rem', paddingTop: '0.8rem', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.85rem', color: isCompleted ? '#888' : '#78ffd6' }}>
                Total: {day.total_calories} kcal
              </div>
            </div>
          </div>
        )})}
        
        {/* Fill empty slots if week is incomplete */}
        {[...Array(7 - weekDays.length)].map((_, i) => (
          <div key={`empty-${i}`} className="cal-day-card" style={{ opacity: 0.3 }}>
            <div className="day-header">
              <span className="day-number">--</span>
            </div>
            <div className="loading-week">End of Plan</div>
          </div>
        ))}
      </div>

      {/* Day Detail Modal */}
      {selectedDay && (
        <DayDetailModal 
          day={selectedDay} 
          onClose={() => setSelectedDay(null)} 
        />
      )}
    </div>
  );
}

export default WeekCalendar;
