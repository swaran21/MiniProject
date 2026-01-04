package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.dto.DietLogRequestDTO;
import com.ai.SpringAIProject.dto.DietRecommendationResponseDTO;
import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

import com.ai.SpringAIProject.dto.UserProfileDTO;
import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;

@RestController
@RequestMapping("/api/diet")
@CrossOrigin(originPatterns = "*")
public class DietController {

    private final MLBridgeService mlService;
    private final UserRepository userRepository;

    public DietController(MLBridgeService mlService, UserRepository userRepository) {
        this.mlService = mlService;
        this.userRepository = userRepository;
    }

    @PostMapping("/recommend")
    public DietRecommendationResponseDTO recommendDiet(@RequestBody DietLogRequestDTO request, @RequestParam(required = false) Long userId) {
        // If userId is provided, fetch profile from DB
        if (userId != null) {
            User user = userRepository.findById(userId).orElse(null);
            if (user != null) {
                UserProfileDTO profile = new UserProfileDTO(
                    user.getWeightKg() != null ? user.getWeightKg() : 70,
                    user.getHeightCm() != null ? user.getHeightCm() : 170,
                    user.getAge() != null ? user.getAge() : 25,
                    user.getGender() != null ? user.getGender() : "M",
                    user.getActivityLevel() != null ? user.getActivityLevel() : "Moderate",
                    user.getHealthGoals() != null ? user.getHealthGoals() : "Balanced",
                    user.getDietaryRestrictions() != null ? user.getDietaryRestrictions() : "None"
                );
                request.setUserProfile(profile);
            }
        }
        return mlService.recommendDiet(request);
    }
}