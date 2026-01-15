package com.ai.SpringAIProject.repository;

import com.ai.SpringAIProject.model.MealPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for MealPlan entity
 * 
 * Provides CRUD operations and custom queries for meal plan management.
 */
@Repository
public interface MealPlanRepository extends JpaRepository<MealPlan, String> {
    
    /**
     * Find the active meal plan for a specific user
     * Each user should only have ONE active plan at a time
     */
    @Query("SELECT m FROM MealPlan m WHERE m.userId = :userId AND m.isActive = true")
    Optional<MealPlan> findActiveByUserId(@Param("userId") Long userId);
    
    /**
     * Find all plans (active and inactive) for a user
     * Useful for plan history
     */
    List<MealPlan> findByUserIdOrderByCreatedAtDesc(Long userId);
    
    /**
     * Find all active plans for a user (should typically be 0 or 1)
     */
    List<MealPlan> findByUserIdAndIsActive(Long userId, Boolean isActive);
    
    /**
     * Check if user has an active plan
     */
    boolean existsByUserIdAndIsActive(Long userId, Boolean isActive);
}
