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
                    response.getId(),  // Include ID for rating functionality
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
            null,  // No ID for fallback
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

    public Object rateRecipe(Long recipeId, String userId, int rating) {
        String url = "http://localhost:5000/predict/recipe/rate?recipe_id=" + recipeId 
                    + "&user_id=" + userId 
                    + "&rating=" + rating;
        
        try {
            return restTemplate.postForObject(url, null, Object.class);
        } catch (Exception e) {
            System.err.println("Error rating recipe: " + e.getMessage());
            return null;
        }
    }

    public Object getRecipeRating(Long recipeId) {
        String url = "http://localhost:5000/predict/recipe/" + recipeId + "/rating";
        
        try {
            return restTemplate.getForObject(url, Object.class);
        } catch (Exception e) {
            System.err.println("Error getting recipe rating: " + e.getMessage());
            return null;
        }
    }

    public Object searchRecipes(String query, int limit) {
        String url = "http://localhost:5000/predict/recipes/search?query=" 
                    + query + "&limit=" + limit;
        
        try {
            return restTemplate.getForObject(url, Object.class);
        } catch (Exception e) {
            System.err.println("Error searching recipes: " + e.getMessage());
            return null;
        }
    }

    public Object getRecipeById(Long recipeId) {
        String url = "http://localhost:5000/predict/recipes/" + recipeId;
        
        try {
            return restTemplate.getForObject(url, Object.class);
        } catch (Exception e) {
            System.err.println("Error getting recipe by ID: " + e.getMessage());
            return null;
        }
    }

    public Object chat(String message) {
        String url = "http://localhost:5000/chat?message=" + message;
        
        try {
            return restTemplate.postForObject(url, null, Object.class);
        } catch (Exception e) {
            System.err.println("Error calling chatbot: " + e.getMessage());
            return null;
        }
    }

    // ===== HEALTH-BASED MEAL PLANNING METHODS =====
    
    public Object analyzePrescription(String prescriptionText, Integer userId) {
        String url = "http://localhost:5000/health/analyze-prescription?prescription_text=" 
                    + prescriptionText;
        if (userId != null) {
            url += "&user_id=" + userId;
        }
        
        try {
            return restTemplate.postForObject(url, null, Object.class);
        } catch (Exception e) {
            System.err.println("Error analyzing prescription: " + e.getMessage());
            return null;
        }
    }
    
    public Object filterRecipesByHealth(java.util.List<String> conditions, Integer minScore, Integer limit) {
        String url = "http://localhost:5000/health/filter-recipes";
        
        java.util.Map<String, Object> request = new java.util.HashMap<>();
        request.put("conditions", conditions);
        request.put("min_score", minScore);
        request.put("limit", limit);
        
        try {
            return restTemplate.postForObject(url, request, Object.class);
        } catch (Exception e) {
            System.err.println("Error filtering recipes: " + e.getMessage());
            return null;
        }
    }
    
    public Object getRecipeHealthScore(Long recipeId, String conditions) {
        String url = "http://localhost:5000/health/recipe-score/" + recipeId 
                    + "?conditions=" + conditions;
        
        try {
            return restTemplate.getForObject(url, Object.class);
        } catch (Exception e) {
            System.err.println("Error getting recipe health score: " + e.getMessage());
            return null;
        }
    }
    
    public Object generateMealPlan(String prescriptionText, java.util.List<String> conditions, 
                                   Integer userId, Integer durationDays) {
        String url = "http://localhost:5000/health/generate-meal-plan";
        
        java.util.Map<String, Object> request = new java.util.HashMap<>();
        if (prescriptionText != null) {
            request.put("prescription_text", prescriptionText);
        }
        if (conditions != null) {
            request.put("conditions", conditions);
        }
        if (userId != null) {
            request.put("user_id", userId);
        }
        if (durationDays != null) {
            request.put("duration_days", durationDays);
        }
        
        try {
            return restTemplate.postForObject(url, request, Object.class);
        } catch (Exception e) {
            System.err.println("Error generating meal plan: " + e.getMessage());
            return null;
        }
    }
}