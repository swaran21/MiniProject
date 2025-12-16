package com.ai.SpringAIProject.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DietRecommendation {
    private int caloriesConsumedEstimate;
    private int caloriesRemaining;
    private String nutritionalAnalysis; // e.g., "High in fats..."
    private String nextMealSuggestion;  // e.g., "Try a Grilled Chicken Salad"
}