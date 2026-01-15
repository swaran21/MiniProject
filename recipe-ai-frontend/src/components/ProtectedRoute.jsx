import React from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute component
 * Wraps components that require authentication
 * Redirects to login if user is not authenticated
 */
const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, user, loading } = useAuth();

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

  if (!isAuthenticated) {
    // Not authenticated - will be handled by App.jsx
    return null;
  }

  // Check for required role if specified
  if (requiredRole && user?.roles) {
    const userRoles = user.roles.split(',').map(r => r.trim());
    if (!userRoles.includes(requiredRole)) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>You don't have permission to access this page.</p>
          <p>Required role: {requiredRole}</p>
        </div>
      );
    }
  }

  return children;
};

export default ProtectedRoute;
