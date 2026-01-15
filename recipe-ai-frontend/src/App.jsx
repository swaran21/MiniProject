import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import HealthProfileComponent from "./components/HealthProfileComponent";
import RecipeComponent from "./components/RecipeComponent";
import MealPlanComponent from "./components/MealPlanComponent";
import DietTrackerComponent from "./components/DietTrackerComponent";
import BrowseRecipes from "./components/BrowseRecipes";
import PrescriptionAnalyzer from "./components/PrescriptionAnalyzer";
import MedicalMealPlanner from "./components/MedicalMealPlanner";
import ChatWidget from "./components/ChatWidget";
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
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        user={user}
        onLogout={handleLogout}
      />
      
      {/* Main Content Area */}

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
        {activeTab === "browse" && (
          <BrowseRecipes />
        )}

        {activeTab === "prescription" && (
          <PrescriptionAnalyzer />
        )}

        {activeTab === "medical-meals" && (
          <MedicalMealPlanner />
        )}

        {activeTab === "mealplan" && (
          <MealPlanComponent user={user} />
        )}
      </main>

      {/* Chat Widget - Always visible */}
      <ChatWidget />
    </div>
  );
}

export default App;