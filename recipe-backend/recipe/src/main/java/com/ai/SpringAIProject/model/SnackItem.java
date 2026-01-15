package com.ai.SpringAIProject.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Snack Item - Embedded class for JSONB storage in PostgreSQL
 * 
 * Represents a single snack item stored in meal_plan_days.snacks column.
 * This class doesn't need @Entity since it's stored as JSONB.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SnackItem implements Serializable {
    
    private Integer recipeId;      // Optional: link to original recipe
    private String title;          // Required: "Almonds", "Greek Yogurt"
    private Integer calories;      // Required: 150
    private Integer healthScore;   // Default: 100
    private String macros;         // Optional: "P:6 C:6 F:14"
}
