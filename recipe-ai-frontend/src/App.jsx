import React, { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
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

function AppContent() {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const [activeTab, setActiveTab] = useState("diet");

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  // If not logged in, show login screen
  // When AuthContext.isAuthenticated changes to true, this re-renders automatically
  if (!isAuthenticated) {
    return <LoginComponent />;
  }

  // Main App (User is logged in)
  return (
    <div className="App">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onLogout={logout}
      />

      <div className="main-content">
        <ChatWidget />

        {activeTab === "diet" && <DietTrackerComponent />}
        {activeTab === "health" && <HealthProfileComponent />}
        {activeTab === "recipe" && <RecipeComponent />}
        {activeTab === "meal-plan" && <MealPlanComponent />}
        {activeTab === "browse" && <BrowseRecipes />}
        {activeTab === "prescription" && <PrescriptionAnalyzer />}
        {activeTab === "medical-meals" && <MedicalMealPlanner />}
      </div>
    </div>
  );
}

// Wrap entire app with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;