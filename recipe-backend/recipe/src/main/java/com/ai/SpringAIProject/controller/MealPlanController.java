package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.dto.*;
import com.ai.SpringAIProject.service.MealPlanService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * REST Controller for Meal Plan Management
 * 
 * Endpoints:
 * - POST   /api/health/meal-plan/save          - Save new meal plan
 * - GET    /api/health/meal-plan/{userId}/active - Get user's active plan
 * - GET    /api/health/meal-plan/{planId}      - Get plan by ID
 * - GET    /api/health/meal-plan/today/{userId} - Get today's meals
 * - DELETE /api/health/meal-plan/{planId}      - Soft delete plan
 */
@RestController
@RequestMapping("/api/health/meal-plan")
@CrossOrigin(origins = "*")
public class MealPlanController {
    
    private final MealPlanService mealPlanService;
    
    public MealPlanController(MealPlanService mealPlanService) {
        this.mealPlanService = mealPlanService;
    }
    
    /**
     * Save a new meal plan (Idempotent)
     * 
     * POST /api/health/meal-plan/save
     * 
     * If a plan with the same ID already exists, returns the existing plan
     * instead of throwing a duplicate key error.
     * 
     * Request Body: SaveMealPlanRequest
     * Response: MealPlanResponse (201 Created or 200 OK if already exists)
     */
    @PostMapping("/save")
    public ResponseEntity<MealPlanResponse> saveMealPlan(
            @Valid @RequestBody SaveMealPlanRequest request) {
        
        try {
            // Check if plan already exists (idempotent operation)
            String planId = request.getPlanData().getPlanId();
            
            if (planId != null && !planId.isEmpty()) {
                var existingPlan = mealPlanService.getPlanById(planId);
                
                if (existingPlan.isPresent()) {
                    // Plan already exists, return it with 200 OK
                    System.out.println("Meal plan " + planId + " already exists. Returning existing plan.");
                    return ResponseEntity.ok(existingPlan.get());
                }
            }
            
            // Plan doesn't exist, save new plan
            MealPlanResponse response = mealPlanService.saveMealPlan(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
            
        } catch (Exception e) {
            // Log error (in production, use proper logging)
            System.err.println("Error saving meal plan: " + e.getMessage());
            throw new RuntimeException("Failed to save meal plan: " + e.getMessage());
        }
    }
    
    /**
     * Get user's active meal plan
     * 
     * GET /api/health/meal-plan/{userId}/active
     * 
     * Response: MealPlanResponse (200 OK) or 404 Not Found
     */
    @GetMapping("/{userId}/active")
    public ResponseEntity<MealPlanResponse> getActivePlan(@PathVariable Long userId) {
        
        return mealPlanService.getActivePlan(userId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * Get meal plan by ID
     * 
     * GET /api/health/meal-plan/{planId}
     * 
     * Response: MealPlanResponse (200 OK) or 404 Not Found
     */
    @GetMapping("/{planId}")
    public ResponseEntity<MealPlanResponse> getPlanById(@PathVariable String planId) {
        
        return mealPlanService.getPlanById(planId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * Get today's meals for a user
     * 
     * GET /api/health/meal-plan/today/{userId}
     * 
     * Response: MealPlanDayResponse (200 OK) or 404 Not Found
     */
    @GetMapping("/today/{userId}")
    public ResponseEntity<MealPlanDayResponse> getTodaysMeals(@PathVariable Long userId) {
        
        return mealPlanService.getTodaysMeals(userId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * Get specific day from a plan
     * 
     * GET /api/health/meal-plan/{planId}/day/{dayNumber}
     * 
     * Response: MealPlanDayResponse (200 OK) or 404 Not Found
     */
    @GetMapping("/{planId}/day/{dayNumber}")
    public ResponseEntity<MealPlanDayResponse> getDayByNumber(
            @PathVariable String planId,
            @PathVariable Integer dayNumber) {
        
        return mealPlanService.getDayByNumber(planId, dayNumber)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * Delete (deactivate) a meal plan
     * 
     * DELETE /api/health/meal-plan/{planId}
     * 
     * Response: Success message (200 OK) or 404 Not Found
     */
    @DeleteMapping("/{planId}")
    public ResponseEntity<Map<String, String>> deletePlan(@PathVariable String planId) {
        
        boolean deleted = mealPlanService.deletePlan(planId);
        
        if (deleted) {
            Map<String, String> response = new HashMap<>();
            response.put("message", "Meal plan deactivated successfully");
            response.put("planId", planId);
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * Check if user has an active plan
     * 
     * GET /api/health/meal-plan/{userId}/has-active
     * 
     * Response: { "hasActivePlan": true/false }
     */
    @GetMapping("/{userId}/has-active")
    public ResponseEntity<Map<String, Boolean>> hasActivePlan(@PathVariable Long userId) {
        
        boolean hasActive = mealPlanService.hasActivePlan(userId);
        
        Map<String, Boolean> response = new HashMap<>();
        response.put("hasActivePlan", hasActive);
        
        return ResponseEntity.ok(response);
    }
}
