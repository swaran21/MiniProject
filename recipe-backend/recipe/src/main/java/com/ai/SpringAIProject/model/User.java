package com.ai.SpringAIProject.model;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password;

    // --- Profile Data ---
    private Double weightKg;
    private Double heightCm;
    private Integer age;
    private String gender; // M/F
    private String activityLevel; // Sedentary, Moderate, Active
    private String healthGoals; // Lose Weight, Balanced, Gain Muscle
    private String dietaryRestrictions; // None, Keto, Vegan
}
