package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
@CrossOrigin(originPatterns = "*")
public class HealthController {

    private final MLBridgeService mlService;

    public HealthController(MLBridgeService mlService) {
        this.mlService = mlService;
    }

    @PostMapping("/analyze-prescription")
    public Object analyzePrescription(@RequestParam String prescriptionText, 
                                     @RequestParam(required = false) Integer userId) {
        System.out.println("Analyzing prescription for user: " + userId);
        return mlService.analyzePrescription(prescriptionText, userId);
    }

    @PostMapping("/filter-recipes")
    public Object filterRecipesByHealth(@RequestBody Map<String, Object> request) {
        @SuppressWarnings("unchecked")
        List<String> conditions = (List<String>) request.get("conditions");
        Integer minScore = (Integer) request.getOrDefault("min_score", 70);
        Integer limit = (Integer) request.getOrDefault("limit", 50);
        
        System.out.println("Filtering recipes for conditions: " + conditions);
        return mlService.filterRecipesByHealth(conditions, minScore, limit);
    }

    @GetMapping("/recipe-score/{recipeId}")
    public Object getRecipeHealthScore(@PathVariable Long recipeId, 
                                       @RequestParam String conditions) {
        System.out.println("Getting health score for recipe: " + recipeId);
        return mlService.getRecipeHealthScore(recipeId, conditions);
    }

    @PostMapping("/generate-meal-plan")
    public Object generateMealPlan(@RequestBody Map<String, Object> request) {
        String prescriptionText = (String) request.get("prescription_text");
        @SuppressWarnings("unchecked")
        List<String> conditions = (List<String>) request.get("conditions");
        Integer userId = (Integer) request.get("user_id");
        Integer durationDays = (Integer) request.get("duration_days");
        
        System.out.println("Generating meal plan for user: " + userId);
        return mlService.generateMealPlan(prescriptionText, conditions, userId, durationDays);
    }

    @PostMapping("/analyze-profile")
    public Map<String, Object> analyzeProfile(@RequestBody Map<String, String> profile) {
        try {
            double weight = Double.parseDouble(profile.get("weightKg"));
            double height = Double.parseDouble(profile.get("heightCm"));
            int age = Integer.parseInt(profile.get("age"));
            String gender = profile.get("gender");
            String activity = profile.get("activityLevel");
            String goal = profile.get("healthGoals");

            // 1. Calculate BMI
            double heightM = height / 100.0;
            double bmi = weight / (heightM * heightM);
            String bmiCategory;
            if (bmi < 18.5) bmiCategory = "Underweight";
            else if (bmi < 25) bmiCategory = "Normal Weight";
            else if (bmi < 30) bmiCategory = "Overweight";
            else bmiCategory = "Obese";

            // 2. Calculate BMR (Mifflin-St Jeor)
            double bmr;
            if ("M".equalsIgnoreCase(gender)) {
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
            } else {
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
            }

            // 3. Activity Multiplier
            double multiplier = 1.2; // Sedentary
            if ("Moderate".equalsIgnoreCase(activity)) multiplier = 1.55;
            else if ("Active".equalsIgnoreCase(activity)) multiplier = 1.725;

            double tdee = bmr * multiplier;

            // 4. Goal Adjustment
            if ("Lose Weight".equalsIgnoreCase(goal)) tdee -= 500;
            else if ("Gain Muscle".equalsIgnoreCase(goal)) tdee += 300;

            return Map.of(
                "bmi", String.format("%.1f", bmi),
                "bmiCategory", bmiCategory,
                "dailyCalorieNeeds", (int) tdee,
                "recommendation", "Based on your goal to " + goal + ", aim for " + (int)tdee + " calories/day."
            );
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Invalid profile data: " + e.getMessage());
        }
    }
}
