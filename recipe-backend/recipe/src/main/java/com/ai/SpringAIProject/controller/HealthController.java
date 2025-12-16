package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.model.UserHealthProfile;
import com.ai.SpringAIProject.service.HealthService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/health")
@CrossOrigin(originPatterns = "*") // Allow React Frontend to access this
public class HealthController {

    private final HealthService healthService;

    public HealthController(HealthService healthService) {
        this.healthService = healthService;
    }

    @PostMapping("/analyze")
    public Map<String, Object> analyzeHealth(@RequestBody UserHealthProfile profile) {
        System.out.println("Health Analysis Request for: " + profile.getHealthGoals());
        return healthService.analyzeHealth(profile);
    }
}