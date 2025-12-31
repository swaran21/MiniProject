package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.dto.MealPlanResponseDTO;
import com.ai.SpringAIProject.dto.UserProfileDTO;
import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/meal-plan")
@CrossOrigin(originPatterns = "*")
public class MealPlanController {

    private final MLBridgeService mlService;

    public MealPlanController(MLBridgeService mlService) {
        this.mlService = mlService;
    }

    @PostMapping("/generate")
    public MealPlanResponseDTO generateMealPlan(@RequestBody UserProfileDTO profile) {
        return mlService.generateMealPlan(profile);
    }
}