package com.ai.SpringAIProject.model;

import lombok.Data;

@Data
public class UserHealthProfile {
    private double weightKg;
    private double heightCm;
    private int age;
    private String gender; // "M", "F", "Other"
    private String activityLevel; // "Sedentary", "Active", etc.
    private String dietaryRestrictions; // "Vegan", "Gluten-Free"
    private String healthGoals; // "Lose Weight", "Gain Muscle"
}