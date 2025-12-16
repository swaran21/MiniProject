package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.model.Meal;
import com.ai.SpringAIProject.model.MealPlan;
import com.ai.SpringAIProject.model.UserHealthProfile;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class MealPlanService {

    public MealPlan generateMealPlan(UserHealthProfile profile) {
        List<Meal> meals = new ArrayList<>();
        String goal = profile.getHealthGoals();
        int targetCalories = 2000; // Default

        // Simple Rule-Based Logic (Mock AI)
        if ("Lose Weight".equalsIgnoreCase(goal)) {
            targetCalories = 1500;
            meals.add(new Meal("Green Smoothie", "Breakfast", 250, "P:10g C:30g"));
            meals.add(new Meal("Grilled Chicken Salad", "Lunch", 450, "P:40g C:10g"));
            meals.add(new Meal("Steamed Fish with Veggies", "Dinner", 400, "P:35g C:5g"));
        } else if ("Gain Muscle".equalsIgnoreCase(goal)) {
            targetCalories = 3000;
            meals.add(new Meal("Eggs & Oatmeal", "Breakfast", 600, "P:30g C:60g"));
            meals.add(new Meal("Steak & Rice", "Lunch", 900, "P:50g C:80g"));
            meals.add(new Meal("Pasta with Meat Sauce", "Dinner", 800, "P:40g C:90g"));
        } else {
            // Maintenance / Balanced
            meals.add(new Meal("Avocado Toast", "Breakfast", 400, "P:12g C:40g"));
            meals.add(new Meal("Turkey Sandwich", "Lunch", 550, "P:30g C:50g"));
            meals.add(new Meal("Stir Fry Tofu", "Dinner", 500, "P:20g C:45g"));
        }

        // Add a snack for everyone
        meals.add(new Meal("Greek Yogurt", "Snack", 150, "P:15g C:10g"));

        // Calculate total
        int currentTotal = meals.stream().mapToInt(Meal::getCalories).sum();

        return new MealPlan(
                goal != null ? goal : "Balanced Diet",
                currentTotal,
                meals,
                "Remember to stay hydrated and eat at regular intervals!"
        );
    }
}