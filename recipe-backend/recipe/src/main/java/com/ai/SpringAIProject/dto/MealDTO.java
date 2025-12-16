package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class MealDTO {
    private String name;
    private String type;
    private int calories;
    private String macros;
}
