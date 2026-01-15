package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Response DTO for meal plan queries
 * 
 * Used for:
 * - GET /api/health/meal-plan/{userId}/active
 * - GET /api/health/meal-plan/{planId}
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MealPlanResponse {
    
    private String planId;
    private Long userId;
    private List<String> conditions;
    private Integer durationDays;
    private String startDate;  // ISO format: "2026-01-15"
    private String endDate;
    private Boolean isActive;
    private String summary;
    private Integer totalDaysCompleted;
    
    private List<MealPlanDayResponse> dailyMeals;
}
