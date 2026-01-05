package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.ArrayList;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DietRecommendationResponseDTO {
    private int caloriesConsumedEstimate;
    private int caloriesRemaining;
    private String nutritionalAnalysis;
    private String nextMealSuggestion;
    private List<RecommendedMealDTO> dayPlan = new ArrayList<>();  // Add structured meal plan
}
