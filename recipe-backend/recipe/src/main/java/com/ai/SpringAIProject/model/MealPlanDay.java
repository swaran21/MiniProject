package com.ai.SpringAIProject.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDate;
import java.util.List;

/**
 * Meal Plan Day Entity - Stores daily meals with SNAPSHOT data
 * 
 * Uses the "snapshot pattern" - stores complete recipe data (title, calories, macros)
 * directly in this table to prevent "ghost recipe" issues if original recipes change.
 */
@Entity
@Table(name = "meal_plan_days", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"plan_id", "day_number"})
})
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MealPlanDay {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "day_id")
    private Long dayId;
    
    // Relationship: Many Days belong to One Plan
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "plan_id", nullable = false)
    private MealPlan mealPlan;
    
    @Column(name = "day_number", nullable = false)
    private Integer dayNumber;  // Day 1, Day 2, etc.
    
    @Column(name = "day_date", nullable = false)
    private LocalDate dayDate;  // Actual calendar date
    
    // ===== BREAKFAST SNAPSHOT =====
    @Column(name = "breakfast_recipe_id")
    private Integer breakfastRecipeId;
    
    @Column(name = "breakfast_title", nullable = false)
    private String breakfastTitle;
    
    @Column(name = "breakfast_calories", nullable = false)
    private Integer breakfastCalories;
    
    @Column(name = "breakfast_health_score")
    private Integer breakfastHealthScore = 100;
    
    @Column(name = "breakfast_macros", length = 50)
    private String breakfastMacros;  // "P:15 C:60 F:10"
    
    // ===== LUNCH SNAPSHOT =====
    @Column(name = "lunch_recipe_id")
    private Integer lunchRecipeId;
    
    @Column(name = "lunch_title", nullable = false)
    private String lunchTitle;
    
    @Column(name = "lunch_calories", nullable = false)
    private Integer lunchCalories;
    
    @Column(name = "lunch_health_score")
    private Integer lunchHealthScore = 100;
    
    @Column(name = "lunch_macros", length = 50)
    private String lunchMacros;  // "P:30 C:50 F:15"
    
    // ===== DINNER SNAPSHOT =====
    @Column(name = "dinner_recipe_id")
    private Integer dinnerRecipeId;
    
    @Column(name = "dinner_title", nullable = false)
    private String dinnerTitle;
    
    @Column(name = "dinner_calories", nullable = false)
    private Integer dinnerCalories;
    
    @Column(name = "dinner_health_score")
    private Integer dinnerHealthScore = 100;
    
    @Column(name = "dinner_macros", length = 50)
    private String dinnerMacros;  // "P:35 C:40 F:20"
    
    // ===== SNACKS (JSON array) =====
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "snacks", columnDefinition = "jsonb")
    private List<SnackItem> snacks;  // [{"title":"Almonds", "calories":150}]
    
    // ===== DAILY TOTALS =====
    @Column(name = "total_calories", nullable = false)
    private Integer totalCalories;
    
    @Column(name = "total_macros", length = 50)
    private String totalMacros;  // "P:86 C:156 F:59"
    
    @Column(name = "created_at", updatable = false)
    private LocalDate createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
    }
}
