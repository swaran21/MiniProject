import React, { useState } from 'react';
import './Sidebar.css';

function Sidebar({ activeTab, setActiveTab, user, onLogout }) {
  const [showDropdown, setShowDropdown] = useState(false);

  const menuItems = [
    { id: 'health', label: 'Health Tracker', icon: '📊' },
    { id: 'diet', label: 'Smart Diet', icon: '🥗' },
    { id: 'recipe', label: 'Recipe Generator', icon: '🧑‍🍳' },
    { id: 'browse', label: 'Browse Recipes', icon: '🔍' },
    { id: 'meal-plan', label: 'Meal Planner', icon: '❤️' },
    { id: 'prescription', label: 'Prescription', icon: '🏥' },
    { id: 'medical-meals', label: 'Medical Meals', icon: '💊' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        NutriChef AI ⚡
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-link ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* User Profile with Dropdown */}
      <div className="sidebar-user">
        {user && (
          <>
            <div 
              className="user-info" 
              onClick={() => setShowDropdown(!showDropdown)}
              style={{ cursor: 'pointer' }}
            >
              <div className="user-avatar">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Welcome back</div>
                <div style={{ fontWeight: 'bold' }}>{user.username}</div>
              </div>
              <span style={{ fontSize: '1.2rem', transition: 'transform 0.3s', transform: showDropdown ? 'rotate(180deg)' : 'rotate(0deg)' }}>
                ▼
              </span>
            </div>

            {/* Dropdown Menu */}
            {showDropdown && (
              <div className="profile-dropdown">
                <div className="dropdown-item" onClick={() => setActiveTab('health')}>
                  <span className="dropdown-icon">👤</span>
                  <span>My Profile</span>
                </div>
                <div className="dropdown-item" onClick={() => setActiveTab('health')}>
                  <span className="dropdown-icon">⚙️</span>
                  <span>Settings</span>
                </div>
                <div className="dropdown-divider"></div>
                <div className="dropdown-item logout" onClick={onLogout}>
                  <span className="dropdown-icon">🚪</span>
                  <span>Logout</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
