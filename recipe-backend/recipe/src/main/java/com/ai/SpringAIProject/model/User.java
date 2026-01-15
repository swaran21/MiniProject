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

    // --- Authentication Fields ---
    @Column(nullable = false)
    private String roles = "USER";  // USER, ADMIN (comma-separated for multiple roles)
    
    @Column(nullable = false)
    private Boolean enabled = true;  // Account enabled/disabled
    
    @Column(updatable = false)
    private java.time.LocalDateTime createdAt;

    // --- Profile Data ---
    private Double weightKg;
    private Double heightCm;
    private Integer age;
    private String gender; // M/F
    private String activityLevel; // Sedentary, Moderate, Active
    private String healthGoals; // Lose Weight, Balanced, Gain Muscle
    private String dietaryRestrictions; // None, Keto, Vegan
    
    @PrePersist
    protected void onCreate() {
        createdAt = java.time.LocalDateTime.now();
        if (enabled == null) enabled = true;
        if (roles == null) roles = "USER";
    }
}
