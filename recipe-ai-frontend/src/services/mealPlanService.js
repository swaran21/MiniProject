import apiClient from '../utils/apiClient';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

/**
 * Save a meal plan to the backend
 * Wraps the plan data in the expected DTO structure
 */
export const saveMealPlan = async (mealPlanData, userId) => {
  const response = await apiClient.post('/api/health/meal-plan/create', {
    userId: userId,
    planData: mealPlanData
  });
  return response.data;
};

/**
 * Get the active meal plan for a user
 */
export const getActiveMealPlan = async (userId) => {
  const response = await apiClient.get(`/api/health/meal-plan/${userId}/active`);
  return response.data;
};

/**
 * Delete a meal plan by ID
 */
export const deleteMealPlan = async (planId) => {
  const response = await apiClient.delete(`/api/health/meal-plan/${planId}`);
  return response.data;
};

/**
 * Toggle the completion status of a meal plan day
 */
export const toggleDayCompletion = async (dayId) => {
  const response = await apiClient.post(`/api/health/meal-plan/day/${dayId}/toggle-complete`);
  return response.data;
};
