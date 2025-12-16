package com.ai.SpringAIProject.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class Meal {
    private String name;        // e.g., "Oatmeal with Berries"
    private String type;        // e.g., "Breakfast", "Lunch", "Dinner", "Snack"
    private int calories;       // e.g., 350
    private String macros;      // e.g., "Protein: 12g, Carbs: 45g"
}