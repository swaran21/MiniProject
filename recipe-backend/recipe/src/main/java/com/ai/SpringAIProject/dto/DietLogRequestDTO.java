package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DietLogRequestDTO {
    private String foodItem;
    private String mealType;
    private UserProfileDTO userProfile;
}
