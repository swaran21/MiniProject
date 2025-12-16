package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.model.DietLog;
import com.ai.SpringAIProject.model.DietRecommendation;
import org.springframework.stereotype.Service;

@Service
public class AdaptiveDietService {

    private final HealthService healthService;

    public AdaptiveDietService(HealthService healthService) {
        this.healthService = healthService;
    }

    public DietRecommendation analyzeAndRecommend(DietLog log) {
        // 1. Get User's Total Daily Needs
        int dailyTarget = healthService.calculateDailyCalories(log.getUserProfile());

        // 2. Estimate Calories of the food eaten (Mocking ML)
        int eatenCalories = estimateCalories(log.getFoodItem());
        String nutrientType = detectNutrientType(log.getFoodItem());

        // 3. Calculate Remaining Budget
        int remaining = dailyTarget - eatenCalories;

        // 4. Generate Logic
        String analysis;
        String suggestion;

        if (eatenCalories > (dailyTarget * 0.4)) {
            analysis = "That was a heavy meal (" + eatenCalories + " kcal). You used a large portion of your daily budget.";
            suggestion = "For your next meal, stick to something light and fiber-rich. \nRecommendation: Green Salad with Lemon Dressing.";
        } else if (nutrientType.equals("Carb-Heavy")) {
            analysis = "Your meal was high in carbohydrates (" + eatenCalories + " kcal).";
            suggestion = "Focus on Protein next to balance blood sugar. \nRecommendation: Grilled Salmon or Tofu Stir-fry.";
        } else if (nutrientType.equals("Protein-Rich")) {
            analysis = "Great protein intake! (" + eatenCalories + " kcal).";
            suggestion = "Ensure you get enough complex carbs next. \nRecommendation: Brown Rice bowl with roasted veggies.";
        } else {
            analysis = "Good balanced choice (" + eatenCalories + " kcal).";
            suggestion = "You are on track! \nRecommendation: A light fruit snack or Greek Yogurt.";
        }

        return new DietRecommendation(eatenCalories, remaining, analysis, suggestion);
    }

    private int estimateCalories(String food) {
        String f = food.toLowerCase();
        if (f.contains("burger") || f.contains("pizza") || f.contains("biryani")) return 850;
        if (f.contains("salad")) return 200;
        if (f.contains("rice")) return 400;
        return 500;
    }

    private String detectNutrientType(String food) {
        String f = food.toLowerCase();
        if (f.contains("rice") || f.contains("pasta") || f.contains("bread") || f.contains("pizza")) return "Carb-Heavy";
        if (f.contains("chicken") || f.contains("egg") || f.contains("meat") || f.contains("fish")) return "Protein-Rich";
        return "Balanced";
    }
}