package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.model.UserHealthProfile;
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

@Service
public class HealthService {

    public Map<String, Object> analyzeHealth(UserHealthProfile profile) {
        Map<String, Object> analysis = new HashMap<>();

        // 0. Safety Check
        if (profile == null || profile.getHeightCm() <= 0 || profile.getWeightKg() <= 0) {
            analysis.put("error", "Invalid Profile Data. Height/Weight must be positive.");
            return analysis;
        }

        // 1. Calculate BMI
        double heightM = profile.getHeightCm() / 100.0;
        double bmi = profile.getWeightKg() / (heightM * heightM);
        analysis.put("bmi", String.format("%.2f", bmi));

        // 2. BMI Category
        String category;
        if (bmi < 18.5) category = "Underweight";
        else if (bmi < 24.9) category = "Normal weight";
        else if (bmi < 29.9) category = "Overweight";
        else category = "Obese";
        analysis.put("bmiCategory", category);

        // 3. Calculate Calories
        int dailyCalorieNeeds = calculateDailyCalories(profile);
        analysis.put("dailyCalorieNeeds", dailyCalorieNeeds);

        return analysis;
    }

    // HELPER: Allows other services to get just the number
    public int calculateDailyCalories(UserHealthProfile profile) {
        double bmr;
        if ("M".equalsIgnoreCase(profile.getGender())) {
            bmr = 88.362 + (13.397 * profile.getWeightKg()) + (4.799 * profile.getHeightCm()) - (5.677 * profile.getAge());
        } else {
            bmr = 447.593 + (9.247 * profile.getWeightKg()) + (3.098 * profile.getHeightCm()) - (4.330 * profile.getAge());
        }

        // Adjust for activity
        double calorieNeeds = bmr * 1.55;

        // Adjust for goal
        if ("Lose Weight".equalsIgnoreCase(profile.getHealthGoals())) {
            calorieNeeds -= 500;
        } else if ("Gain Muscle".equalsIgnoreCase(profile.getHealthGoals())) {
            calorieNeeds += 500;
        }

        return (int) calorieNeeds;
    }
}