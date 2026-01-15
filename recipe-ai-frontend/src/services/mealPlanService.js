const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

/**
 * Save a meal plan to the backend
 * Wraps the plan data in the expected DTO structure
 */
export const saveMealPlan = async (mealPlanData, userId) => {
  const response = await fetch(`${API_BASE_URL}/api/health/meal-plan/save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId: userId,
      planData: mealPlanData
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to save meal plan: ${errorText}`);
  }

  return response.json();
};

/**
 * Get the active meal plan for a user
 */
export const getActiveMealPlan = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/health/meal-plan/${userId}/active`);
  
  if (response.status === 404) {
    return null;
  }
  
  if (!response.ok) {
    throw new Error('Failed to fetch active meal plan');
  }

  return response.json();
};

/**
 * Delete a meal plan by ID
 */
export const deleteMealPlan = async (planId) => {
  const response = await fetch(`${API_BASE_URL}/api/health/meal-plan/${planId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete meal plan');
  }

  return response.json();
};

/**
 * Toggle the completion status of a specific day
 */
export const toggleDayCompletion = async (dayId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health/meal-plan/day/${dayId}/toggle-complete`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Failed to toggle completion: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error toggling completion:", error);
        throw error;
    }
};
