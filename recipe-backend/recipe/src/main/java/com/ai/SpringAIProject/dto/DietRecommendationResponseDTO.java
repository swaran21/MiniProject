package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DietRecommendationResponseDTO {
    private int caloriesConsumedEstimate;
    private int caloriesRemaining;
    private String nutritionalAnalysis;
    private String nextMealSuggestion;
}
