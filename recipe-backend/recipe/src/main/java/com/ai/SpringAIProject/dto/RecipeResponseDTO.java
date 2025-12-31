package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class RecipeResponseDTO {
    private String title;
    private List<String> ingredients;
    private String instructions;
    private String cuisineType;
    private int calories;
    private String imageUrl;
}
