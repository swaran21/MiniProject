package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.dto.*;
import com.ai.SpringAIProject.model.Recipe;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Arrays;
import java.util.List;

@Service
public class MLBridgeService {

    private final RestTemplate restTemplate;

    public MLBridgeService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Recipe generateRecipe(String ingredients, String cuisine, String restrictions) {
        String pythonServiceUrl = "http://localhost:5000/predict/recipe";

        // 1. Create Request DTO
        RecipeRequestDTO request = new RecipeRequestDTO(ingredients, cuisine, restrictions);

        try {
            // 2. Call Python Microservice
            RecipeResponseDTO response = restTemplate.postForObject(pythonServiceUrl, request, RecipeResponseDTO.class);

            if (response != null) {
                // 3. Map DTO to Domain Model
                return new Recipe(
                    response.getTitle(),
                    response.getIngredients(),
                    response.getInstructions(),
                    response.getCuisineType(),
                    response.getCalories(),
                    response.getImageUrl()
                );
            }
        } catch (Exception e) {
            System.err.println("Error calling Python Service: " + e.getMessage());
        }

        // Fallback if service is down / fails
        return new Recipe(
            "Service Unavailable",
            Arrays.asList("Error"),
            "Could not generate recipe. Ensure Python Service is running.",
            "None",
            0,
            ""
        );
    }

    public MealPlanResponseDTO generateMealPlan(UserProfileDTO profile) {
        String url = "http://localhost:5000/predict/meal-plan";
        return restTemplate.postForObject(url, profile, MealPlanResponseDTO.class);
    }

    public DietRecommendationResponseDTO recommendDiet(DietLogRequestDTO request) {
        String url = "http://localhost:5000/predict/adaptive-diet";
        return restTemplate.postForObject(url, request, DietRecommendationResponseDTO.class);
    }

    public List<String> identifyIngredientsFromImage(byte[] imageBytes) {
        // TODO: Send imageBytes to Python Computer Vision Model (YOLO/TensorFlow)
        // For now, return dummy detected ingredients
        return Arrays.asList("Tomato", "Onion", "Green Pepper");
    }
}