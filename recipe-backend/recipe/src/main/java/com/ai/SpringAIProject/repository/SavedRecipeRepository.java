package com.ai.SpringAIProject.repository;

import com.ai.SpringAIProject.model.SavedRecipe;
import com.ai.SpringAIProject.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Repository
public interface SavedRecipeRepository extends JpaRepository<SavedRecipe, Long> {
    
    // Find all recipes saved by a specific user
    List<SavedRecipe> findByUserOrderBySavedAtDesc(User user);
    
    // Find by user ID
    List<SavedRecipe> findByUserIdOrderBySavedAtDesc(Long userId);
    
    // Delete a saved recipe by ID and user ID (for security)
    @Transactional
    @Modifying
    Long deleteByIdAndUserId(Long id, Long userId);
}
