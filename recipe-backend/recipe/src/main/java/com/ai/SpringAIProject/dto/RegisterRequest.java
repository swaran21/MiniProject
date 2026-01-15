package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {
    private String username;
    private String password;
    
    // Profile data (optional during registration)
    private Double weightKg;
    private Double heightCm;
    private Integer age;
    private String gender;
    private String activityLevel;
    private String healthGoals;
    private String dietaryRestrictions;
}
