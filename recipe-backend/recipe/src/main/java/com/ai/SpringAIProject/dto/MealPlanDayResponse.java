package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Response DTO for a single day's meals
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MealPlanDayResponse {
    
    private Integer day;
    private String date;  // ISO format: "2026-01-15"
    
    private MealResponse breakfast;
    private MealResponse lunch;
    private MealResponse dinner;
    private List<MealResponse> snacks;
    
    private Integer totalCalories;
    private String totalMacros;  // "P:86 C:156 F:59"
    private MacrosDTO totalMacrosBreakdown;
}
