package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.dto.DietLogRequestDTO;
import com.ai.SpringAIProject.dto.DietRecommendationResponseDTO;
import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/diet")
@CrossOrigin(originPatterns = "*")
public class DietController {

    private final MLBridgeService mlService;

    public DietController(MLBridgeService mlService) {
        this.mlService = mlService;
    }

    @PostMapping("/recommend")
    public DietRecommendationResponseDTO recommendDiet(@RequestBody DietLogRequestDTO request) {
        return mlService.recommendDiet(request);
    }
}