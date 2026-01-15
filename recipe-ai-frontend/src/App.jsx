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

  const handleLoginSuccess = () => {
    // Login handled by AuthContext, just for compatibility
  };

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
  if (!isAuthenticated) {
    return <LoginComponent onLoginSuccess={handleLoginSuccess} />;
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

        {activeTab === "diet" && <DietTrackerComponent userId={user?.id} />}
        {activeTab === "health" && <HealthProfileComponent userId={user?.id} />}
        {activeTab === "recipe" && <RecipeComponent userId={user?.id} />}
        {activeTab === "meal-plan" && <MealPlanComponent userId={user?.id} />}
        {activeTab === "browse" && <BrowseRecipes userId={user?.id} />}
        {activeTab === "prescription" && <PrescriptionAnalyzer userId={user?.id} />}
        {activeTab === "medical-meals" && <MedicalMealPlanner userId={user?.id} />}
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