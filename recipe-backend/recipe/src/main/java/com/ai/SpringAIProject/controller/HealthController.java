package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
@CrossOrigin(originPatterns = "*")
public class HealthController {

    private final MLBridgeService mlService;

    public HealthController(MLBridgeService mlService) {
        this.mlService = mlService;
    }

    @PostMapping("/analyze-prescription")
    public Object analyzePrescription(@RequestParam String prescriptionText, 
                                     @RequestParam(required = false) Integer userId) {
        System.out.println("Analyzing prescription for user: " + userId);
        return mlService.analyzePrescription(prescriptionText, userId);
    }

    @PostMapping("/filter-recipes")
    public Object filterRecipesByHealth(@RequestBody Map<String, Object> request) {
        @SuppressWarnings("unchecked")
        List<String> conditions = (List<String>) request.get("conditions");
        Integer minScore = (Integer) request.getOrDefault("min_score", 70);
        Integer limit = (Integer) request.getOrDefault("limit", 50);
        
        System.out.println("Filtering recipes for conditions: " + conditions);
        return mlService.filterRecipesByHealth(conditions, minScore, limit);
    }

    @GetMapping("/recipe-score/{recipeId}")
    public Object getRecipeHealthScore(@PathVariable Long recipeId, 
                                       @RequestParam String conditions) {
        System.out.println("Getting health score for recipe: " + recipeId);
        return mlService.getRecipeHealthScore(recipeId, conditions);
    }

    @PostMapping("/generate-meal-plan")
    public Object generateMealPlan(@RequestBody Map<String, Object> request) {
        String prescriptionText = (String) request.get("prescription_text");
        @SuppressWarnings("unchecked")
        List<String> conditions = (List<String>) request.get("conditions");
        Integer userId = (Integer) request.get("user_id");
        Integer durationDays = (Integer) request.get("duration_days");
        
        System.out.println("Generating meal plan for user: " + userId);
        return mlService.generateMealPlan(prescriptionText, conditions, userId, durationDays);
    }
}
