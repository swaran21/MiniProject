package com.ai.SpringAIProject.service.mapper;

import com.ai.SpringAIProject.dto.*;
import com.ai.SpringAIProject.model.MealPlan;
import com.ai.SpringAIProject.model.MealPlanDay;
import com.ai.SpringAIProject.model.SnackItem;
import com.ai.SpringAIProject.service.util.MacrosCalculator;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Mapper for MealPlan DTO ↔ Entity conversions
 * 
 * SINGLE RESPONSIBILITY: Mapping only, no business logic
 * 
 * Handles:
 * - Entity → Response DTO (for API responses)
 * - Request DTO → Entity (for saving)
 */
@Component
public class MealPlanMapper {
    
    private final MacrosCalculator macrosCalculator;
    
    public MealPlanMapper(MacrosCalculator macrosCalculator) {
        this.macrosCalculator = macrosCalculator;
    }
    
    // ===== DTO → ENTITY (Request Mapping) =====
    
    /**
     * Convert DailyMealDTO to MealPlanDay entity
     */
    public MealPlanDay toEntity(SaveMealPlanRequest.DailyMealDTO dayDTO, MealPlan mealPlan) {
        MealPlanDay day = new MealPlanDay();
        day.setMealPlan(mealPlan);
        day.setDayNumber(dayDTO.getDay());
        
        // Set date
        day.setDayDate(dayDTO.getDate() != null ? LocalDate.parse(dayDTO.getDate()) : 
            mealPlan.getStartDate().plusDays(dayDTO.getDay() - 1));
        
        // Map breakfast
        day.setBreakfastRecipeId(dayDTO.getBreakfast().getRecipeId());
        day.setBreakfastTitle(dayDTO.getBreakfast().getTitle());
        day.setBreakfastCalories(dayDTO.getBreakfast().getCalories());
        day.setBreakfastHealthScore(dayDTO.getBreakfast().getHealthScore() != null ? 
            dayDTO.getBreakfast().getHealthScore() : 100);
        day.setBreakfastMacros(extractMacrosFromDTO(dayDTO.getBreakfast()));
        
        // Map lunch
        day.setLunchRecipeId(dayDTO.getLunch().getRecipeId());
        day.setLunchTitle(dayDTO.getLunch().getTitle());
        day.setLunchCalories(dayDTO.getLunch().getCalories());
        day.setLunchHealthScore(dayDTO.getLunch().getHealthScore() != null ? 
            dayDTO.getLunch().getHealthScore() : 100);
        day.setLunchMacros(extractMacrosFromDTO(dayDTO.getLunch()));
        
        // Map dinner
        day.setDinnerRecipeId(dayDTO.getDinner().getRecipeId());
        day.setDinnerTitle(dayDTO.getDinner().getTitle());
        day.setDinnerCalories(dayDTO.getDinner().getCalories());
        day.setDinnerHealthScore(dayDTO.getDinner().getHealthScore() != null ? 
            dayDTO.getDinner().getHealthScore() : 100);
        day.setDinnerMacros(extractMacrosFromDTO(dayDTO.getDinner()));
        
        // Map snacks
        if (dayDTO.getSnacks() != null && !dayDTO.getSnacks().isEmpty()) {
            day.setSnacks(dayDTO.getSnacks().stream()
                .map(this::toSnackEntity)
                .collect(Collectors.toList()));
        }
        
        // Set totals
        day.setTotalCalories(dayDTO.getTotalCalories());
        day.setTotalMacros(calculateDayTotalMacros(day));
        
        return day;
    }
    
    /**
     * Convert MealDTO to SnackItem entity
     */
    private SnackItem toSnackEntity(SaveMealPlanRequest.MealDTO mealDTO) {
        SnackItem snack = new SnackItem();
        snack.setRecipeId(mealDTO.getRecipeId());
        snack.setTitle(mealDTO.getTitle());
        snack.setCalories(mealDTO.getCalories());
        snack.setHealthScore(mealDTO.getHealthScore() != null ? mealDTO.getHealthScore() : 100);
        snack.setMacros(extractMacrosFromDTO(mealDTO));
        return snack;
    }
    
    /**
     * Extract macros from MealDTO - supports 3 formats:
     * 1. Pre-formatted string: "P:20 C:40 F:15"
     * 2. Individual fields: protein, carbs, fats
     * 3. Auto-estimate from calories
     */
    private String extractMacrosFromDTO(SaveMealPlanRequest.MealDTO mealDTO) {
        // Format 1: Already formatted
        if (mealDTO.getMacros() != null && macrosCalculator.isValidMacrosFormat(mealDTO.getMacros())) {
            return mealDTO.getMacros();
        }
        
        // Format 2: Individual fields
        if (mealDTO.getProtein() != null && mealDTO.getCarbs() != null && mealDTO.getFats() != null) {
            return macrosCalculator.formatMacros(
                mealDTO.getProtein(), 
                mealDTO.getCarbs(), 
                mealDTO.getFats()
            );
        }
        
        // Format 3: Estimate from calories
        if (mealDTO.getCalories() != null) {
            return macrosCalculator.estimateMacrosFromCalories(mealDTO.getCalories());
        }
        
        return null;
    }
    
    /**
     * Calculate total macros for entire day
     */
    private String calculateDayTotalMacros(MealPlanDay day) {
        String[] allMacros = new String[]{
            day.getBreakfastMacros(),
            day.getLunchMacros(),
            day.getDinnerMacros()
        };
        
        // Add snack macros
        if (day.getSnacks() != null) {
            String[] snackMacros = day.getSnacks().stream()
                .map(SnackItem::getMacros)
                .toArray(String[]::new);
            
            // Combine meal and snack macros
            String[] combined = new String[allMacros.length + snackMacros.length];
            System.arraycopy(allMacros, 0, combined, 0, allMacros.length);
            System.arraycopy(snackMacros, 0, combined, allMacros.length, snackMacros.length);
            allMacros = combined;
        }
        
        return macrosCalculator.sumMacros(allMacros);
    }
    
    // ===== ENTITY → DTO (Response Mapping) =====
    
    /**
     * Convert MealPlan entity to MealPlanResponse DTO
     */
    public MealPlanResponse toResponse(MealPlan plan) {
        MealPlanResponse response = new MealPlanResponse();
        response.setPlanId(plan.getPlanId());
        response.setUserId(plan.getUserId());
        response.setConditions(plan.getConditions());
        response.setDurationDays(plan.getDurationDays());
        response.setStartDate(plan.getStartDate().toString());
        response.setEndDate(plan.getEndDate().toString());
        response.setIsActive(plan.getIsActive());
        response.setSummary(plan.getSummary());
        response.setTotalDaysCompleted(plan.getTotalDaysCompleted());
        
        List<MealPlanDayResponse> dailyMeals = plan.getDays().stream()
            .sorted(Comparator.comparing(MealPlanDay::getDayNumber))
            .map(this::toDayResponse)
            .collect(Collectors.toList());
        response.setDailyMeals(dailyMeals);
        
        return response;
    }
    
    /**
     * Convert MealPlanDay entity to MealPlanDayResponse DTO
     */
    public MealPlanDayResponse toDayResponse(MealPlanDay day) {
        MealPlanDayResponse response = new MealPlanDayResponse();
        response.setDay(day.getDayNumber());
        response.setDate(day.getDayDate().toString());
        
        // Convert meals
        response.setBreakfast(toMealResponse(
            day.getBreakfastRecipeId(), day.getBreakfastTitle(),
            day.getBreakfastCalories(), day.getBreakfastHealthScore(), day.getBreakfastMacros()));
        
        response.setLunch(toMealResponse(
            day.getLunchRecipeId(), day.getLunchTitle(),
            day.getLunchCalories(), day.getLunchHealthScore(), day.getLunchMacros()));
        
        response.setDinner(toMealResponse(
            day.getDinnerRecipeId(), day.getDinnerTitle(),
            day.getDinnerCalories(), day.getDinnerHealthScore(), day.getDinnerMacros()));
        
        // Convert snacks
        if (day.getSnacks() != null && !day.getSnacks().isEmpty()) {
            response.setSnacks(day.getSnacks().stream()
                .map(snack -> toMealResponse(snack.getRecipeId(), snack.getTitle(),
                    snack.getCalories(), snack.getHealthScore(), snack.getMacros()))
                .collect(Collectors.toList()));
        }
        
        // Totals
        response.setTotalCalories(day.getTotalCalories());
        response.setTotalMacros(day.getTotalMacros());
        response.setTotalMacrosBreakdown(MacrosDTO.fromString(day.getTotalMacros()));
        
        return response;
    }
    
    /**
     * Convert meal data to MealResponse DTO
     */
    private MealResponse toMealResponse(Integer recipeId, String title, Integer calories,
                                       Integer healthScore, String macros) {
        MealResponse response = new MealResponse();
        response.setRecipeId(recipeId);
        response.setTitle(title);
        response.setCalories(calories);
        response.setHealthScore(healthScore);
        response.setMacros(macros);
        response.setMacrosBreakdown(MacrosDTO.fromString(macros));
        return response;
    }
}
