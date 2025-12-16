package com.ai.SpringAIProject.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DietLog {
    private String foodItem;       // e.g., "Cheeseburger"
    private String mealType;       // e.g., "Lunch"
    private UserHealthProfile userProfile; // Context for personalization
}