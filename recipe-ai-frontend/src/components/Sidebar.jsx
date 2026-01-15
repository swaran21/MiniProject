import React from 'react';
import './Sidebar.css';

function Sidebar({ activeTab, setActiveTab, user, onLogout }) {
  const menuItems = [
    { id: 'health', label: 'Health Tracker', icon: '📊' },
    { id: 'diet', label: 'Smart Diet', icon: '🥗' },
    { id: 'recipe', label: 'Recipe Generator', icon: '🧑‍🍳' },
    { id: 'browse', label: 'Browse Recipes', icon: '🔍' },
    { id: 'mealplan', label: 'Meal Planner', icon: '❤️' },
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

      {user && (
        <div className="sidebar-user">
          <div className="user-info">
            <div className="user-avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Welcome back</div>
              <div style={{ fontWeight: 'bold' }}>{user.username}</div>
            </div>
          </div>
          <button onClick={onLogout} className="logout-btn">
            Logout 🚪
          </button>
        </div>
      )}
    </div>
  );
}

export default Sidebar;
