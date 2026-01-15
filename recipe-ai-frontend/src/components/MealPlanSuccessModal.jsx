import React from 'react';
import './MealPlanSuccessModal.css';

function MealPlanSuccessModal({ onOpenCalendar, onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <span className="modal-icon">🎉</span>
        <h2 className="modal-title">Plan Saved Successfully!</h2>
        <p className="modal-text">
          Your personalized medical meal plan is ready. <br/>
          Switch to Calendar View to track your daily progress.
        </p>
        
        <div className="modal-actions">
          <button className="btn-calendar" onClick={onOpenCalendar}>
            📅 Open Calendar View
          </button>
          <button className="btn-close" onClick={onClose}>
            Stay Here
          </button>
        </div>
      </div>
    </div>
  );
}

export default MealPlanSuccessModal;
