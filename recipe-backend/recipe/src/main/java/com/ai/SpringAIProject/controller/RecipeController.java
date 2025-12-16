package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.model.Recipe;
import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/recipes")
@CrossOrigin(originPatterns = "*") // Allow React Frontend to access this
public class RecipeController {

    private final MLBridgeService mlService;

    public RecipeController(MLBridgeService mlService) {
        this.mlService = mlService;
    }

    @GetMapping("/generate")
    public Recipe generateRecipe(@RequestParam String ingredients,
                                 @RequestParam(defaultValue = "any") String cuisine,
                                 @RequestParam(defaultValue = "") String dietaryRestrictions) {
        System.out.println("Generating Recipe for: " + ingredients);
        return mlService.generateRecipe(ingredients, cuisine, dietaryRestrictions);
    }

    // Endpoint for the "Snap to Link" feature (Abstract Outcome 3)
    // Note: React would send a file here, simplified for now
    @PostMapping("/identify-ingredients")
    public String identifyIngredients() {
        return "Feature coming soon: Will process image via Python ML";
    }
}