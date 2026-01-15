package com.ai.SpringAIProject.repository;

import com.ai.SpringAIProject.model.MealPlanDay;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Repository for MealPlanDay entity
 * 
 * Provides CRUD operations and queries for individual meal plan days.
 */
@Repository
public interface MealPlanDayRepository extends JpaRepository<MealPlanDay, Long> {
    
    /**
     * Find all days for a specific meal plan
     */
    @Query("SELECT d FROM MealPlanDay d WHERE d.mealPlan.planId = :planId ORDER BY d.dayNumber")
    List<MealPlanDay> findByPlanIdOrderByDayNumber(@Param("planId") String planId);
    
    /**
     * Find a specific day within a plan
     */
    @Query("SELECT d FROM MealPlanDay d WHERE d.mealPlan.planId = :planId AND d.dayNumber = :dayNumber")
    Optional<MealPlanDay> findByPlanIdAndDayNumber(@Param("planId") String planId, @Param("dayNumber") Integer dayNumber);
    
    /**
     * Find day by actual calendar date
     * Useful for "show me today's meals"
     */
    @Query("SELECT d FROM MealPlanDay d WHERE d.mealPlan.planId = :planId AND d.dayDate = :date")
    Optional<MealPlanDay> findByPlanIdAndDate(@Param("planId") String planId, @Param("date") LocalDate date);
    
    /**
     * Get total number of days in a plan
     */
    long countByMealPlan_PlanId(String planId);
}
