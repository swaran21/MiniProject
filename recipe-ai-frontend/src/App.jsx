import React, { useState } from "react";
import Navbar from "./components/Navbar";
import HealthProfileComponent from "./components/HealthProfileComponent";
import RecipeComponent from "./components/RecipeComponent";
import MealPlanComponent from "./components/MealPlanComponent";
import DietTrackerComponent from "./components/DietTrackerComponent";
import LoginComponent from "./components/LoginComponent";
import "./App.css";

function App() {
  // --- Global Auth State ---
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("diet");

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  // Check localStorage on mount
  React.useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  // If not logged in, show login screen
  if (!user) {
    return <LoginComponent onLoginSuccess={handleLoginSuccess} />;
  }

  // Main App (User is logged in)
  return (
    <div className="App">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* User Info Bar */}
      <div style={{ 
        background: "#667eea", 
        color: "white", 
        padding: "10px 20px", 
        display: "flex", 
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <span>👤 Welcome, <strong>{user.username}</strong></span>
        <button 
          onClick={handleLogout}
          style={{
            background: "white",
            color: "#667eea",
            border: "none",
            padding: "5px 15px",
            borderRadius: "5px",
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          Logout
        </button>
      </div>

      <main className="main-content">
        {activeTab === "health" && (
          <HealthProfileComponent 
            user={user} 
            onUpdateProfile={(updated) => {
              const updatedUser = {...user, ...updated};
              setUser(updatedUser);
              localStorage.setItem("user", JSON.stringify(updatedUser));
            }} 
          />
        )}
        {activeTab === "diet" && (
          <DietTrackerComponent user={user} />
        )}
        {activeTab === "recipe" && <RecipeComponent user={user} />}
        {activeTab === "mealplan" && (
          <MealPlanComponent user={user} />
        )}
      </main>
    </div>
  );
}

export default App;