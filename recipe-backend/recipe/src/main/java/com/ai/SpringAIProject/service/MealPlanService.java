package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.model.MealPlan;
import com.ai.SpringAIProject.model.MealPlanDay;
import com.ai.SpringAIProject.model.SnackItem;
import com.ai.SpringAIProject.repository.MealPlanDayRepository;
import com.ai.SpringAIProject.repository.MealPlanRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

/**
 * PRODUCTION-READY Service for managing meal plans
 * 
 * Features:
 * - Parses Python's JSON response and persists to PostgreSQL
 * - FULL MACROS INTEGRATION (Protein, Carbs, Fats) - handles 4 input formats!
 * - Uses BOTH repositories (cascade for saves, dayRepository for queries)
 * - Automatic macros estimation from calories
 * - Complete round-trip JSON conversion
 */
@Service
public class MealPlanService {
    
    private final MealPlanRepository mealPlanRepository;
    private final MealPlanDayRepository mealPlanDayRepository;  // NOW ACTUALLY USED!
    
    public MealPlanService(MealPlanRepository mealPlanRepository, 
                          MealPlanDayRepository mealPlanDayRepository) {
        this.mealPlanRepository = mealPlanRepository;
        this.mealPlanDayRepository = mealPlanDayRepository;
    }
    
    /**
     * Save a meal plan from Python's JSON response
     */
    @Transactional
    public MealPlan saveMealPlan(Map<String, Object> pythonResponse, Long userId) {
        String planId = (String) pythonResponse.getOrDefault("plan_id", generatePlanId());
        Integer durationDays = (Integer) pythonResponse.get("duration_days");
        String summary = (String) pythonResponse.get("summary");
        
        @SuppressWarnings("unchecked")
        List<String> conditions = (List<String>) pythonResponse.getOrDefault("conditions", new ArrayList<>());
        
        // Deactivate old plan if exists
        mealPlanRepository.findActiveByUserId(userId).ifPresent(oldPlan -> {
            oldPlan.setIsActive(false);
            mealPlanRepository.save(oldPlan);
        });
        
        // Create new plan
        MealPlan mealPlan = new MealPlan();
        mealPlan.setPlanId(planId);
        mealPlan.setUserId(userId);
        mealPlan.setConditions(conditions);
        mealPlan.setDurationDays(durationDays);
        mealPlan.setStartDate(LocalDate.now());
        mealPlan.setEndDate(LocalDate.now().plusDays(durationDays - 1));
        mealPlan.setIsActive(true);
        mealPlan.setSummary(summary);
        mealPlan.setTotalDaysCompleted(0);
        
        // Parse and add days
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> dailyMeals = (List<Map<String, Object>>) pythonResponse.get("daily_meals");
        
        if (dailyMeals != null) {
            for (Map<String, Object> dayData : dailyMeals) {
                MealPlanDay day = parseDayFromJson(dayData, mealPlan);
                mealPlan.addDay(day);
            }
        }
        
        return mealPlanRepository.save(mealPlan); // Cascade saves days
    }
    
    /**
     * Parse day with FULL MACROS extraction
     */
    private MealPlanDay parseDayFromJson(Map<String, Object> dayData, MealPlan mealPlan) {
        MealPlanDay day = new MealPlanDay();
        day.setMealPlan(mealPlan);
        day.setDayNumber((Integer) dayData.get("day"));
        
        // Set date
        String dateStr = (String) dayData.get("date");
        day.setDayDate(dateStr != null ? LocalDate.parse(dateStr) : 
            mealPlan.getStartDate().plusDays(day.getDayNumber() - 1));
        
        // Parse meals with macros
        @SuppressWarnings("unchecked")
        Map<String, Object> breakfast = (Map<String, Object>) dayData.get("breakfast");
        day.setBreakfastRecipeId((Integer) breakfast.get("recipe_id"));
        day.setBreakfastTitle((String) breakfast.get("title"));
        day.setBreakfastCalories((Integer) breakfast.get("calories"));
        day.setBreakfastHealthScore((Integer) breakfast.getOrDefault("health_score", 100));
        day.setBreakfastMacros(extractAndFormatMacros(breakfast));
        
        @SuppressWarnings("unchecked")
        Map<String, Object> lunch = (Map<String, Object>) dayData.get("lunch");
        day.setLunchRecipeId((Integer) lunch.get("recipe_id"));
        day.setLunchTitle((String) lunch.get("title"));
        day.setLunchCalories((Integer) lunch.get("calories"));
        day.setLunchHealthScore((Integer) lunch.getOrDefault("health_score", 100));
        day.setLunchMacros(extractAndFormatMacros(lunch));
        
        @SuppressWarnings("unchecked")
        Map<String, Object> dinner = (Map<String, Object>) dayData.get("dinner");
        day.setDinnerRecipeId((Integer) dinner.get("recipe_id"));
        day.setDinnerTitle((String) dinner.get("title"));
        day.setDinnerCalories((Integer) dinner.get("calories"));
        day.setDinnerHealthScore((Integer) dinner.getOrDefault("health_score", 100));
        day.setDinnerMacros(extractAndFormatMacros(dinner));
        
        // Parse snacks
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> snacksData = (List<Map<String, Object>>) dayData.get("snacks");
        if (snacksData != null && !snacksData.isEmpty()) {
            day.setSnacks(snacksData.stream()
                .map(this::parseSnackFromJson)
                .collect(Collectors.toList()));
        }
        
        day.setTotalCalories((Integer) dayData.get("total_calories"));
        day.setTotalMacros(calculateTotalMacrosForDay(day));  // Calculate!
        
        return day;
    }
    
    private SnackItem parseSnackFromJson(Map<String, Object> snackData) {
        SnackItem snack = new SnackItem();
        snack.setRecipeId((Integer) snackData.get("recipe_id"));
        snack.setTitle((String) snackData.get("title"));
        snack.setCalories((Integer) snackData.get("calories"));
        snack.setHealthScore((Integer) snackData.getOrDefault("health_score", 100));
        snack.setMacros(extractAndFormatMacros(snackData));
        return snack;
    }
    
    /**
     * SMART MACROS EXTRACTION - Handles 4 formats:
     * 1. "P:20 C:40 F:15" (already formatted)
     * 2. {protein: 20, carbs: 40, fats: 15} (individual fields)
     * 3. {macros: {protein: 20, carbs: 40, fats: 15}} (nested)
     * 4. Estimate from calories (30/40/30 ratio)
     */
    private String extractAndFormatMacros(Map<String, Object> mealData) {
        // Format 1: Already formatted string
        if (mealData.containsKey("macros") && mealData.get("macros") instanceof String) {
            String macros = (String) mealData.get("macros");
            if (macros != null && macros.matches("P:\\d+ C:\\d+ F:\\d+")) {
                return macros;
            }
        }
        
        // Format 2: Individual fields
        if (mealData.containsKey("protein") && mealData.containsKey("carbs") && mealData.containsKey("fats")) {
            return String.format("P:%d C:%d F:%d", 
                getIntValue(mealData.get("protein")),
                getIntValue(mealData.get("carbs")),
                getIntValue(mealData.get("fats")));
        }
        
        // Format 3: Nested object
        if (mealData.containsKey("macros") && mealData.get("macros") instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> macrosObj = (Map<String, Object>) mealData.get("macros");
            return String.format("P:%d C:%d F:%d",
                getIntValue(macrosObj.get("protein")),
                getIntValue(macrosObj.get("carbs")),
                getIntValue(macrosObj.get("fats")));
        }
        
        // Format 4: Estimate from calories (30% protein, 40% carbs, 30% fats)
        if (mealData.containsKey("calories")) {
            int calories = getIntValue(mealData.get("calories"));
            int protein = (int) Math.round((calories * 0.30) / 4.0);  // 4 cal/g
            int carbs = (int) Math.round((calories * 0.40) / 4.0);    // 4 cal/g
            int fats = (int) Math.round((calories * 0.30) / 9.0);     // 9 cal/g
            return String.format("P:%d C:%d F:%d", protein, carbs, fats);
        }
        
        return null;
    }
    
    /**
     * Calculate TOTAL macros for entire day (breakfast + lunch + dinner + snacks)
     */
    private String calculateTotalMacrosForDay(MealPlanDay day) {
        int totalProtein = 0, totalCarbs = 0, totalFats = 0;
        
        // Sum breakfast
        if (day.getBreakfastMacros() != null) {
            int[] m = parseMacrosString(day.getBreakfastMacros());
            totalProtein += m[0]; totalCarbs += m[1]; totalFats += m[2];
        }
        
        // Sum lunch
        if (day.getLunchMacros() != null) {
            int[] m = parseMacrosString(day.getLunchMacros());
            totalProtein += m[0]; totalCarbs += m[1]; totalFats += m[2];
        }
        
        // Sum dinner
        if (day.getDinnerMacros() != null) {
            int[] m = parseMacrosString(day.getDinnerMacros());
            totalProtein += m[0]; totalCarbs += m[1]; totalFats += m[2];
        }
        
        // Sum snacks
        if (day.getSnacks() != null) {
            for (SnackItem snack : day.getSnacks()) {
                if (snack.getMacros() != null) {
                    int[] m = parseMacrosString(snack.getMacros());
                    totalProtein += m[0]; totalCarbs += m[1]; totalFats += m[2];
                }
            }
        }
        
        return String.format("P:%d C:%d F:%d", totalProtein, totalCarbs, totalFats);
    }
    
    /**
     * Parse "P:20 C:40 F:15" → [20, 40, 15]
     */
    private int[] parseMacrosString(String macros) {
        int[] result = new int[3];
        if (macros == null || macros.isEmpty()) return result;
        
        try {
            for (String part : macros.split("\\s+")) {
                if (part.startsWith("P:")) result[0] = Integer.parseInt(part.substring(2));
                else if (part.startsWith("C:")) result[1] = Integer.parseInt(part.substring(2));
                else if (part.startsWith("F:")) result[2] = Integer.parseInt(part.substring(2));
            }
        } catch (Exception e) {
            System.err.println("Error parsing macros: " + macros);
        }
        return result;
    }
    
    private int getIntValue(Object value) {
        if (value == null) return 0;
        if (value instanceof Integer) return (Integer) value;
        if (value instanceof Double) return ((Double) value).intValue();
        if (value instanceof String) {
            try { return Integer.parseInt((String) value); } 
            catch (NumberFormatException e) { return 0; }
        }
        return 0;
    }
    
    // ===== QUERY METHODS - NOW USING dayRepository! =====
    
    @Transactional(readOnly = true)
    public Optional<MealPlan> getActivePlan(Long userId) {
        Optional<MealPlan> planOpt = mealPlanRepository.findActiveByUserId(userId);
        planOpt.ifPresent(plan -> plan.getDays().size()); // Force load
        return planOpt;
    }
    
    @Transactional(readOnly = true)
    public Optional<MealPlan> getPlanById(String planId) {
        Optional<MealPlan> planOpt = mealPlanRepository.findById(planId);
        planOpt.ifPresent(plan -> plan.getDays().size());
        return planOpt;
    }
    
    /**
     * Get specific day - USING dayRepository!
     */
    @Transactional(readOnly = true)
    public Optional<MealPlanDay> getDayByNumber(String planId, Integer dayNumber) {
        return mealPlanDayRepository.findByPlanIdAndDayNumber(planId, dayNumber);
    }
    
    /**
     * Get TODAY's meals - USING dayRepository!
     */
    @Transactional(readOnly = true)
    public Optional<MealPlanDay> getTodaysMeals(Long userId) {
        return mealPlanRepository.findActiveByUserId(userId)
            .flatMap(plan -> mealPlanDayRepository.findByPlanIdAndDate(plan.getPlanId(), LocalDate.now()));
    }
    
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
    
    public boolean hasActivePlan(Long userId) {
        return mealPlanRepository.existsByUserIdAndIsActive(userId, true);
    }
    
    private String generatePlanId() {
        return "PLAN_" + java.time.LocalDateTime.now()
            .format(java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
    }
    
    /**
     * Convert to JSON with FULL MACROS BREAKDOWN
     */
    public Map<String, Object> toJsonResponse(MealPlan plan) {
        Map<String, Object> response = new HashMap<>();
        response.put("plan_id", plan.getPlanId());
        response.put("user_id", plan.getUserId());
        response.put("conditions", plan.getConditions());
        response.put("duration_days", plan.getDurationDays());
        response.put("start_date", plan.getStartDate().toString());
        response.put("end_date", plan.getEndDate().toString());
        response.put("is_active", plan.getIsActive());
        response.put("summary", plan.getSummary());
        response.put("total_days_completed", plan.getTotalDaysCompleted());
        
        List<Map<String, Object>> dailyMeals = plan.getDays().stream()
            .sorted(Comparator.comparing(MealPlanDay::getDayNumber))
            .map(this::dayToJson)
            .collect(Collectors.toList());
        response.put("daily_meals", dailyMeals);
        
        return response;
    }
    
    private Map<String, Object> dayToJson(MealPlanDay day) {
        Map<String, Object> json = new HashMap<>();
        json.put("day", day.getDayNumber());
        json.put("date", day.getDayDate().toString());
        
        // Each meal with macros STRING and BREAKDOWN object
        json.put("breakfast", mealToJson(
            day.getBreakfastRecipeId(), day.getBreakfastTitle(),
            day.getBreakfastCalories(), day.getBreakfastHealthScore(), day.getBreakfastMacros()));
        
        json.put("lunch", mealToJson(
            day.getLunchRecipeId(), day.getLunchTitle(),
            day.getLunchCalories(), day.getLunchHealthScore(), day.getLunchMacros()));
        
        json.put("dinner", mealToJson(
            day.getDinnerRecipeId(), day.getDinnerTitle(),
            day.getDinnerCalories(), day.getDinnerHealthScore(), day.getDinnerMacros()));
        
        if (day.getSnacks() != null && !day.getSnacks().isEmpty()) {
            json.put("snacks", day.getSnacks().stream()
                .map(s -> mealToJson(s.getRecipeId(), s.getTitle(), s.getCalories(), 
                    s.getHealthScore(), s.getMacros()))
                .collect(Collectors.toList()));
        }
        
        json.put("total_calories", day.getTotalCalories());
        json.put("total_macros", day.getTotalMacros());
        json.put("total_macros_breakdown", parseMacrosToObject(day.getTotalMacros()));
        
        return json;
    }
    
    private Map<String, Object> mealToJson(Integer recipeId, String title, Integer calories, 
                                           Integer healthScore, String macros) {
        Map<String, Object> meal = new HashMap<>();
        meal.put("recipe_id", recipeId);
        meal.put("title", title);
        meal.put("calories", calories);
        meal.put("health_score", healthScore);
        meal.put("macros", macros);
        meal.put("macros_breakdown", parseMacrosToObject(macros));
        return meal;
    }
    
    /**
     * Parse "P:20 C:40 F:15" → {protein: 20, carbs: 40, fats: 15}
     */
    private Map<String, Integer> parseMacrosToObject(String macros) {
        Map<String, Integer> result = new HashMap<>();
        int[] parsed = parseMacrosString(macros);
        result.put("protein", parsed[0]);
        result.put("carbs", parsed[1]);
        result.put("fats", parsed[2]);
        return result;
    }
}
