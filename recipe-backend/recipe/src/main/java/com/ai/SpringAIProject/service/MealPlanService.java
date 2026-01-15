package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.dto.*;
import com.ai.SpringAIProject.model.MealPlan;
import com.ai.SpringAIProject.model.MealPlanDay;
import com.ai.SpringAIProject.repository.MealPlanDayRepository;
import com.ai.SpringAIProject.repository.MealPlanRepository;
import com.ai.SpringAIProject.service.mapper.MealPlanMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.Optional;

/**
 * REFACTORED Service - SINGLE RESPONSIBILITY: Business Logic Only
 * 
 * Responsibilities:
 * ✅ Meal plan CRUD operations
 * ✅ Business rules (one active plan per user, soft deletes)
 * ✅ Database persistence coordination
 * 
 * Delegated to other classes:
 * ❌ DTO mapping → MealPlanMapper
 * ❌ Macros calculations → MacrosCalculator
 * 
 * SOLID Principles Applied:
 * - Single Responsibility Principle (SRP)
 * - Dependency Inversion (depends on abstractions via repositories)
 */
@Service
public class MealPlanService {
    
    private final MealPlanRepository mealPlanRepository;
    private final MealPlanDayRepository mealPlanDayRepository;
    private final MealPlanMapper mapper;
    
    public MealPlanService(
            MealPlanRepository mealPlanRepository,
            MealPlanDayRepository mealPlanDayRepository,
            MealPlanMapper mapper) {
        this.mealPlanRepository = mealPlanRepository;
        this.mealPlanDayRepository = mealPlanDayRepository;
        this.mapper = mapper;
    }
    
    /**
     * Save a meal plan (creates new, deactivates old)
     * 
     * Business Rule: Only ONE active plan per user
     */
    @Transactional
    public MealPlanResponse saveMealPlan(SaveMealPlanRequest request) {
        Long userId = request.getUserId();
        SaveMealPlanRequest.MealPlanDataDTO planData = request.getPlanData();
        
        // Generate plan ID if not provided
        String planId = planData.getPlanId() != null ? planData.getPlanId() : generatePlanId();
        
        // Business Rule: Deactivate old plan if exists
        deactivateExistingPlan(userId);
        
        // Create new plan entity
        MealPlan mealPlan = createMealPlanEntity(planId, userId, planData);
        
        // Add days using mapper
        if (planData.getDailyMeals() != null) {
            for (SaveMealPlanRequest.DailyMealDTO dayDTO : planData.getDailyMeals()) {
                MealPlanDay day = mapper.toEntity(dayDTO, mealPlan);
                mealPlan.addDay(day);
            }
        }
        
        // Save and return response DTO
        MealPlan savedPlan = mealPlanRepository.save(mealPlan);
        return mapper.toResponse(savedPlan);
    }
    
    /**
     * Get active meal plan for a user
     */
    @Transactional(readOnly = true)
    public Optional<MealPlanResponse> getActivePlan(Long userId) {
        return mealPlanRepository.findActiveByUserId(userId)
            .map(plan -> {
                plan.getDays().size(); // Force lazy load
                return mapper.toResponse(plan);
            });
    }
    
    /**
     * Get meal plan by ID
     */
    @Transactional(readOnly = true)
    public Optional<MealPlanResponse> getPlanById(String planId) {
        return mealPlanRepository.findById(planId)
            .map(plan -> {
                plan.getDays().size(); // Force lazy load
                return mapper.toResponse(plan);
            });
    }
    
    /**
     * Get specific day from a plan
     */
    @Transactional(readOnly = true)
    public Optional<MealPlanDayResponse> getDayByNumber(String planId, Integer dayNumber) {
        return mealPlanDayRepository.findByPlanIdAndDayNumber(planId, dayNumber)
            .map(mapper::toDayResponse);
    }
    
    /**
     * Get today's meals for a user
     */
    @Transactional(readOnly = true)
    public Optional<MealPlanDayResponse> getTodaysMeals(Long userId) {
        return mealPlanRepository.findActiveByUserId(userId)
            .flatMap(plan -> mealPlanDayRepository.findByPlanIdAndDate(
                plan.getPlanId(), LocalDate.now()))
            .map(mapper::toDayResponse);
    }
    
    /**
     * Soft delete a meal plan (set isActive = false)
     * 
     * Business Rule: Soft delete to preserve history
     */
    @Transactional
    public boolean deletePlan(String planId) {
        return mealPlanRepository.findById(planId)
            .map(plan -> {
                plan.setIsActive(false);
                mealPlanRepository.save(plan);
                return true;
            })
            .orElse(false);
    }
    
    /**
     * Check if user has an active plan
     */
    public boolean hasActivePlan(Long userId) {
        return mealPlanRepository.existsByUserIdAndIsActive(userId, true);
    }
    
    // ===== PRIVATE HELPER METHODS (Business Logic Only) =====
    
    /**
     * Deactivate existing active plan for user
     */
    private void deactivateExistingPlan(Long userId) {
        mealPlanRepository.findActiveByUserId(userId).ifPresent(oldPlan -> {
            oldPlan.setIsActive(false);
            mealPlanRepository.save(oldPlan);
        });
    }
    
    /**
     * Create MealPlan entity from request data
     */
    private MealPlan createMealPlanEntity(String planId, Long userId, 
                                         SaveMealPlanRequest.MealPlanDataDTO planData) {
        MealPlan mealPlan = new MealPlan();
        mealPlan.setPlanId(planId);
        mealPlan.setUserId(userId);
        mealPlan.setConditions(planData.getConditions());
        mealPlan.setDurationDays(planData.getDurationDays());
        mealPlan.setStartDate(LocalDate.now());
        mealPlan.setEndDate(LocalDate.now().plusDays(planData.getDurationDays() - 1));
        mealPlan.setIsActive(true);
        mealPlan.setSummary(planData.getSummary());
        mealPlan.setTotalDaysCompleted(0);
        return mealPlan;
    }
    
    /**
     * Generate unique plan ID
     */
    private String generatePlanId() {
        return "PLAN_" + LocalDate.now().format(
            java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd")) 
            + "_" + System.currentTimeMillis();
    }
}
