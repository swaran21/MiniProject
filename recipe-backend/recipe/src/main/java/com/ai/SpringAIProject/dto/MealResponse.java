package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for individual meal (breakfast/lunch/dinner/snack)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MealResponse {
    
    private Integer recipeId;
    private String title;
    private Integer calories;
    private Integer healthScore;
    
    // Macros in both formats for flexibility
    private String macros;  // "P:20 C:40 F:15" - for storage/display
    private MacrosDTO macrosBreakdown;  // {protein: 20, carbs: 40, fats: 15} - for charts/UI
}
