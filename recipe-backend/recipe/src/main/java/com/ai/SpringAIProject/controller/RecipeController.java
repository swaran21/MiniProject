package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.model.Recipe;
import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;
import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/recipes")
@CrossOrigin(originPatterns = "*")
public class RecipeController {

    private final MLBridgeService mlService;
    private final UserRepository userRepository;

    public RecipeController(MLBridgeService mlService, UserRepository userRepository) {
        this.mlService = mlService;
        this.userRepository = userRepository;
    }

    @GetMapping("/generate")
    public Recipe generateRecipe(@RequestParam String ingredients,
                                 @RequestParam(defaultValue = "any") String cuisine,
                                 @RequestParam(defaultValue = "") String dietaryRestrictions,
                                 @RequestParam(required = false) Long userId) {
        
        // If userId is provided, fetch user's dietary preferences
        String finalRestrictions = dietaryRestrictions;
        if (userId != null) {
            User user = userRepository.findById(userId).orElse(null);
            if (user != null && user.getDietaryRestrictions() != null) {
                finalRestrictions = user.getDietaryRestrictions();
            }
        }
        
        System.out.println("Generating Recipe for: " + ingredients + " (User: " + userId + ")");
        return mlService.generateRecipe(ingredients, cuisine, finalRestrictions);
    }

    @PostMapping("/{recipeId}/rate")
    public Object rateRecipe(@PathVariable Long recipeId,
                            @RequestParam int rating,
                            @RequestParam(required = false) Long userId) {
        // Default to anonymous user if userId not provided
        String userIdString = userId != null ? userId.toString() : "anonymous";
        
        System.out.println("Rating recipe " + recipeId + " with rating " + rating + " by user " + userIdString);
        return mlService.rateRecipe(recipeId, userIdString, rating);
    }

    @GetMapping("/{recipeId}/rating")
    public Object getRecipeRating(@PathVariable Long recipeId) {
        return mlService.getRecipeRating(recipeId);
    }

    @PostMapping("/identify-ingredients")
    public String identifyIngredients() {
        return "Feature coming soon: Will process image via Python ML";
    }
}
