import React from "react";

function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav className="navbar">
      <div className="logo">NutriChef AI 🥗</div>
      <div className="nav-links">
        <button 
          className={activeTab === "health" ? "active" : ""} 
          onClick={() => setActiveTab("health")}
        >
          Health Tracker
        </button>
        
        {/* NEW BUTTON */}
        <button 
          className={activeTab === "diet" ? "active" : ""} 
          onClick={() => setActiveTab("diet")}
        >
          Smart Diet
        </button>

        <button 
          className={activeTab === "recipe" ? "active" : ""} 
          onClick={() => setActiveTab("recipe")}
        >
          Recipe Generator
        </button>
        
        <button 
          className={activeTab === "mealplan" ? "active" : ""} 
          onClick={() => setActiveTab("mealplan")}
        >
          Meal Planner
        </button>
      </div>
    </nav>
  );
}

export default Navbar;