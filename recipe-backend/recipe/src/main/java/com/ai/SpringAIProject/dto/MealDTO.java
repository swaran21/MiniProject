package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.ArrayList;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class MealDTO {
    private String name;
    private String type;  // Breakfast, Lunch, Dinner, Snack
    private int calories;
    private String macros;
    private List<String> ingredients = new ArrayList<>();  // Add ingredients from Python
    private String instructions = "";  // Add instructions from Python
}
