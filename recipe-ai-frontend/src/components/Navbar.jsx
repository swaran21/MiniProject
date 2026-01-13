import React from "react";

function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav className="navbar">
      <div className="logo">NutriChef AI 🥗</div>
      <div className="nav-links">
        <button 
          className={`nav-link ${activeTab === "health" ? "active" : ""}`} 
          onClick={() => setActiveTab("health")}
        >
          Health Tracker
        </button>
        
        {/* NEW BUTTON */}
        <button 
          className={`nav-link ${activeTab === "diet" ? "active" : ""}`} 
          onClick={() => setActiveTab("diet")}
        >
          Smart Diet
        </button>

        <button 
          className={`nav-link ${activeTab === "recipe" ? "active" : ""}`} 
          onClick={() => setActiveTab("recipe")}
        >
          Recipe Generator
        </button>
        
        <button 
          className={`nav-link ${activeTab === "browse" ? "active" : ""}`} 
          onClick={() => setActiveTab("browse")}
        >
          Browse Recipes
        </button>
        
        <button 
          className={`nav-link ${activeTab === "mealplan" ? "active" : ""}`} 
          onClick={() => setActiveTab("mealplan")}
        >
          Meal Planner
        </button>
        
        <button 
          className={`nav-link ${activeTab === "prescription" ? "active" : ""}`} 
          onClick={() => setActiveTab("prescription")}
        >
          🏥 Prescription
        </button>
        
        <button 
          className={`nav-link ${activeTab === "medical-meals" ? "active" : ""}`} 
          onClick={() => setActiveTab("medical-meals")}
        >
          🍽️ Medical Meals
        </button>
      </div>
    </nav>
  );
}

export default Navbar;