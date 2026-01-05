package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class RecommendedMealDTO {
    private String type;  // Breakfast, Lunch, Dinner, Snack
    private RecipeResponseDTO recipe;
    private String suggestionReason;
}
