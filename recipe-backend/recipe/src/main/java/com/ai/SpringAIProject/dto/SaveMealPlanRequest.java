package com.ai.SpringAIProject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import java.util.List;

/**
 * Request DTO for saving a meal plan
 * 
 * This is sent from:
 * 1. Frontend (when user clicks "Save Plan")
 * 2. Python service (after generating plan)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SaveMealPlanRequest {
    
    @NotNull(message = "User ID is required")
    private Long userId;
    
    @NotNull(message = "Meal plan data is required")
    private MealPlanDataDTO planData;
    
    /**
     * Nested DTO for plan metadata + daily meals
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MealPlanDataDTO {
        
        @JsonProperty("plan_id")
        private String planId;  // Optional - will be generated if not provided
        
        @NotNull(message = "Duration is required")
        @Min(value = 1, message = "Duration must be at least 1 day")
        @JsonProperty("duration_days")
        private Integer durationDays;
        
        private String summary;
        
        private List<String> conditions;  // ["diabetes_type2", "hypertension"]
        
        @NotNull(message = "Daily meals are required")
        @JsonProperty("daily_meals")
        private List<DailyMealDTO> dailyMeals;
    }
    
    /**
     * DTO for a single day's meals
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DailyMealDTO {
        
        @NotNull(message = "Day number is required")
        private Integer day;
        
        private String date;  // Optional - will be calculated if not provided
        
        @NotNull(message = "Breakfast is required")
        private MealDTO breakfast;
        
        @NotNull(message = "Lunch is required")
        private MealDTO lunch;
        
        @NotNull(message = "Dinner is required")
        private MealDTO dinner;
        
        private List<MealDTO> snacks;
        
        @NotNull(message = "Total calories required")
        @JsonProperty("total_calories")
        private Integer totalCalories;
    }
    
    /**
     * DTO for individual meal (breakfast/lunch/dinner/snack)
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MealDTO {
        
        @JsonProperty("recipe_id")
        private Integer recipeId;
        
        @NotNull(message = "Meal title is required")
        private String title;
        
        @NotNull(message = "Calories are required")
        @Min(value = 0, message = "Calories cannot be negative")
        private Integer calories;
        
        @JsonProperty("health_score")
        private Integer healthScore;  // Default to 100 if not provided
        
        // Macros can be:
        // 1. String: "P:20 C:40 F:15"
        // 2. Object with individual fields
        // 3. null (will be estimated from calories)
        private String macros;
        
        // Alternative: individual macro fields
        private Integer protein;
        private Integer carbs;
        private Integer fats;
    }
}
