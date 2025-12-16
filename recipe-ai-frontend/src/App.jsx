import React, { useState } from "react";
import Navbar from "./components/Navbar";
import HealthProfileComponent from "./components/HealthProfileComponent";
import RecipeComponent from "./components/RecipeComponent";
import MealPlanComponent from "./components/MealPlanComponent";
import DietTrackerComponent from "./components/DietTrackerComponent";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("health");

  return (
    <div className="App">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        {activeTab === "health" && <HealthProfileComponent />}
        {activeTab === "diet" && <DietTrackerComponent />}
        {activeTab === "recipe" && <RecipeComponent />}
        {activeTab === "mealplan" && <MealPlanComponent />}
      </main>
    </div>
  );
}

export default App;