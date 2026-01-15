// Meal Plan API Service - Frontend Integration
// Connects React frontend to Java backend meal plan endpoints

const API_BASE_URL = 'http://localhost:8080/api/health/meal-plan';

/**
 * Save a meal plan to the database
 * @param {Object} mealPlanData - The meal plan data from Python generation
 * @param {number} userId - The user ID
 * @returns {Promise<Object>} Saved meal plan response
 */
export const saveMealPlan = async (mealPlanData, userId) => {
  try {
    const requestBody = {
      userId: userId,
      planData: {
        planId: mealPlanData.plan_id,
        durationDays: mealPlanData.duration_days,
        summary: mealPlanData.summary,
        conditions: mealPlanData.conditions || [],
        dailyMeals: mealPlanData.daily_meals || []
      }
    };

    const response = await fetch(`${API_BASE_URL}/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`Failed to save meal plan: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error saving meal plan:', error);
    throw error;
  }
};

/**
 * Get the active meal plan for a user
 * @param {number} userId - The user ID
 * @returns {Promise<Object|null>} Active meal plan or null if none exists
 */
export const getActiveMealPlan = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${userId}/active`);
    
    if (response.status === 404) {
      return null; // No active plan found
    }
    
    if (!response.ok) {
      throw new Error(`Failed to fetch active plan: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching active meal plan:', error);
    throw error;
  }
};

/**
 * Get a specific meal plan by ID
 * @param {string} planId - The plan ID
 * @returns {Promise<Object|null>} Meal plan or null if not found
 */
export const getMealPlanById = async (planId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${planId}`);
    
    if (response.status === 404) {
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`Failed to fetch meal plan: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching meal plan by ID:', error);
    throw error;
  }
};

/**
 * Get today's meals for a user
 * @param {number} userId - The user ID
 * @returns {Promise<Object|null>} Today's meals or null if none
 */
export const getTodaysMeals = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/today/${userId}`);
    
    if (response.status === 404) {
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`Failed to fetch today's meals: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching today's meals:", error);
    throw error;
  }
};

/**
 * Get a specific day from a meal plan
 * @param {string} planId - The plan ID
 * @param {number} dayNumber - The day number (1-based)
 * @returns {Promise<Object|null>} Day's meals or null if not found
 */
export const getDayByNumber = async (planId, dayNumber) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${planId}/day/${dayNumber}`);
    
    if (response.status === 404) {
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`Failed to fetch day: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching day by number:', error);
    throw error;
  }
};

/**
 * Delete (deactivate) a meal plan
 * @param {string} planId - The plan ID to delete
 * @returns {Promise<boolean>} True if deleted successfully
 */
export const deleteMealPlan = async (planId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${planId}`, {
      method: 'DELETE'
    });
    
    if (response.status === 404) {
      throw new Error('Meal plan not found');
    }
    
    if (!response.ok) {
      throw new Error(`Failed to delete meal plan: ${response.statusText}`);
    }

    return true;
  } catch (error) {
    console.error('Error deleting meal plan:', error);
    throw error;
  }
};

/**
 * Check if user has an active meal plan
 * @param {number} userId - The user ID
 * @returns {Promise<boolean>} True if user has an active plan
 */
export const hasActivePlan = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${userId}/has-active`);
    
    if (!response.ok) {
      throw new Error(`Failed to check active plan: ${response.statusText}`);
    }

    const data = await response.json();
    return data.hasActivePlan;
  } catch (error) {
    console.error('Error checking active plan:', error);
    return false;
  }
};
