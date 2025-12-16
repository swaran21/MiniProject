package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class UserProfileDTO {
    private double weightKg;
    private double heightCm;
    private int age;
    private String gender;
    private String activityLevel;
    private String healthGoals;
    private String dietaryRestrictions;
}
