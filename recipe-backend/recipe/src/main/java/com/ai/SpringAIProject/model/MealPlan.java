package com.ai.SpringAIProject.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import java.util.List;

@Data
@AllArgsConstructor
public class MealPlan {
    private String goal;             // e.g., "Weight Loss"
    private int totalDailyCalories;  // e.g., 1800
    private List<Meal> meals;        // List of Breakfast, Lunch, Dinner
    private String suggestion;       // AI advice, e.g., "Drink 3L of water today."
}