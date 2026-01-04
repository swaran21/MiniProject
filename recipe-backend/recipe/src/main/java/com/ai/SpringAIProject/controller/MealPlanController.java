package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.dto.MealPlanResponseDTO;
import com.ai.SpringAIProject.dto.UserProfileDTO;
import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;
import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/meal-plan")
@CrossOrigin(originPatterns = "*")
public class MealPlanController {

    private final MLBridgeService mlService;
    private final UserRepository userRepository;

    public MealPlanController(MLBridgeService mlService, UserRepository userRepository) {
        this.mlService = mlService;
        this.userRepository = userRepository;
    }

    @PostMapping("/generate")
    public MealPlanResponseDTO generateMealPlan(@RequestBody(required = false) UserProfileDTO profile,
                                                @RequestParam(required = false) Long userId) {
        
        // If userId is provided, fetch profile from DB
        UserProfileDTO finalProfile = profile;
        if (userId != null) {
            User user = userRepository.findById(userId).orElse(null);
            if (user != null) {
                finalProfile = new UserProfileDTO(
                    user.getWeightKg() != null ? user.getWeightKg() : 70,
                    user.getHeightCm() != null ? user.getHeightCm() : 170,
                    user.getAge() != null ? user.getAge() : 25,
                    user.getGender() != null ? user.getGender() : "M",
                    user.getActivityLevel() != null ? user.getActivityLevel() : "Moderate",
                    user.getHealthGoals() != null ? user.getHealthGoals() : "Balanced",
                    user.getDietaryRestrictions() != null ? user.getDietaryRestrictions() : "None"
                );
            }
        }
        
        return mlService.generateMealPlan(finalProfile);
    }
}
