import React, { useState } from "react";

const API_BASE_URL = "http://localhost:8080";

function LoginComponent({ onLoginSuccess }) {
  const [authMode, setAuthMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [profileData, setProfileData] = useState({
    weightKg: "", heightCm: "", age: "", gender: "M",
    activityLevel: "Moderate", healthGoals: "Balanced", dietaryRestrictions: "None"
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAuth = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const endpoint = authMode === "login" ? "/api/auth/login" : "/api/auth/register";
    const payload = authMode === "login" 
      ? { username, password }
      : { username, password, ...profileData };

    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || "Authentication failed");
      }

      const userData = await res.json();
      onLoginSuccess(userData);
    } catch (err) {
      setError(err.message || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    }}>
      <div className="component-card" style={{ maxWidth: "450px", width: "90%" }}>
        <div style={{ textAlign: "center", marginBottom: "30px" }}>
          <h1 style={{ fontSize: "2.5rem", margin: "0 0 10px 0" }}>🍽️ NutriChef AI</h1>
          <p style={{ color: "#666", margin: 0 }}>Your Personal AI Nutrition Assistant</p>
        </div>

        <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
          🔐 {authMode === "login" ? "Welcome Back" : "Create Your Profile"}
        </h2>

        <form onSubmit={handleAuth}>
          <div className="form-group">
            <label>Username</label>
            <input 
              type="text" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              required 
              placeholder="Enter your username"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              placeholder="Enter your password"
            />
          </div>

          {authMode === "register" && (
            <div style={{ background: "#f8f9fa", padding: "15px", borderRadius: "8px", marginBottom: "15px" }}>
              <h4 style={{ margin: "0 0 15px 0" }}>Your Health Profile</h4>
              
              <div className="grid-form" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label>Age</label>
                  <input 
                    type="number" 
                    placeholder="25" 
                    value={profileData.age} 
                    onChange={e => setProfileData({...profileData, age: e.target.value})} 
                    required
                  />
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label>Gender</label>
                  <select 
                    value={profileData.gender} 
                    onChange={e => setProfileData({...profileData, gender: e.target.value})}
                  >
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                  </select>
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label>Weight (kg)</label>
                  <input 
                    type="number" 
                    placeholder="70" 
                    value={profileData.weightKg} 
                    onChange={e => setProfileData({...profileData, weightKg: e.target.value})} 
                    required
                  />
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label>Height (cm)</label>
                  <input 
                    type="number" 
                    placeholder="170" 
                    value={profileData.heightCm} 
                    onChange={e => setProfileData({...profileData, heightCm: e.target.value})} 
                    required
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginTop: "10px" }}>
                <label>Health Goal</label>
                <select 
                  value={profileData.healthGoals} 
                  onChange={e => setProfileData({...profileData, healthGoals: e.target.value})}
                >
                  <option value="Balanced">Balanced Diet</option>
                  <option value="Lose Weight">Lose Weight</option>
                  <option value="Gain Muscle">Gain Muscle</option>
                </select>
              </div>

              <div className="form-group">
                <label>Activity Level</label>
                <select 
                  value={profileData.activityLevel} 
                  onChange={e => setProfileData({...profileData, activityLevel: e.target.value})}
                >
                  <option value="Sedentary">Sedentary</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Active">Active</option>
                </select>
              </div>
            </div>
          )}

          {error && (
            <div style={{ 
              background: "#fee", 
              border: "1px solid #fcc", 
              padding: "10px", 
              borderRadius: "5px", 
              marginBottom: "15px",
              color: "#c33"
            }}>
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="action-button full-width" 
            disabled={loading}
            style={{ marginTop: "10px" }}
          >
            {loading ? "Processing..." : (authMode === "login" ? "Login" : "Create Account")}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: "20px", fontSize: "0.9rem" }}>
          {authMode === "login" ? "Don't have an account?" : "Already have an account?"}
          {" "}
          <span 
            onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}
            style={{ color: "#667eea", cursor: "pointer", fontWeight: "bold" }}
          >
            {authMode === "login" ? "Register" : "Login"}
          </span>
        </p>
      </div>
    </div>
  );
}

export default LoginComponent;
