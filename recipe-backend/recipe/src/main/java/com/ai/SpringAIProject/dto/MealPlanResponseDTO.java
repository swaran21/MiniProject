package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class MealPlanResponseDTO {
    private String goal;
    private int totalDailyCalories;
    private String suggestion;
    private List<MealDTO> meals;
}
