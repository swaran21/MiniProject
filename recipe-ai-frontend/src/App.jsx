import React, { useState } from "react";
import Navbar from "./components/Navbar";
import HealthProfileComponent from "./components/HealthProfileComponent";
import RecipeComponent from "./components/RecipeComponent";
import MealPlanComponent from "./components/MealPlanComponent";
import DietTrackerComponent from "./components/DietTrackerComponent";
import "./App.css";

// Default Profile
const DEFAULT_PROFILE = {
  weightKg: "",
  heightCm: "",
  age: "",
  gender: "M",
  activityLevel: "Moderate",
  healthGoals: "Balanced",
  dietaryRestrictions: "None"
};

function App() {
  const [activeTab, setActiveTab] = useState("health");

  // Load from LocalStorage
  const [userProfile, setUserProfile] = useState(() => {
    const saved = localStorage.getItem("userProfile");
    return saved ? JSON.parse(saved) : DEFAULT_PROFILE;
  });

  // Save to LocalStorage
  const handleProfileUpdate = (newProfile) => {
    setUserProfile(newProfile);
    localStorage.setItem("userProfile", JSON.stringify(newProfile));
  };

  return (
    <div className="App">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        {activeTab === "health" && (
          <HealthProfileComponent 
            userProfile={userProfile} 
            onUpdateProfile={handleProfileUpdate} 
          />
        )}
        {activeTab === "diet" && (
          <DietTrackerComponent userProfile={userProfile} />
        )}
        {activeTab === "recipe" && <RecipeComponent />}
        {activeTab === "mealplan" && (
          <MealPlanComponent userProfile={userProfile} />
        )}
      </main>
    </div>
  );
}

export default App;