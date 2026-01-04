package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.model.SavedRecipe;
import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.SavedRecipeRepository;
import com.ai.SpringAIProject.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/recipes")
@CrossOrigin(origins = "http://localhost:5173")
public class SavedRecipeController {
    
    @Autowired
    private SavedRecipeRepository savedRecipeRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @PostMapping("/save")
    public ResponseEntity<?> saveRecipe(@RequestParam Long userId, @RequestBody Map<String, Object> recipeData) {
        try {
            // Find user
            User user = userRepository.findById(userId)
                    .orElseThrow(() -> new RuntimeException("User not found"));
            
            // Create SavedRecipe
            SavedRecipe savedRecipe = new SavedRecipe();
            savedRecipe.setUser(user);
            savedRecipe.setRecipeTitle((String) recipeData.get("title"));
            savedRecipe.setRecipeJson(objectMapper.writeValueAsString(recipeData));
            
            // Save
            SavedRecipe saved = savedRecipeRepository.save(savedRecipe);
            
            return ResponseEntity.ok(Map.of(
                "message", "Recipe saved successfully!",
                "id", saved.getId()
            ));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/saved")
    public ResponseEntity<?> getSavedRecipes(@RequestParam Long userId) {
        try {
            List<SavedRecipe> recipes = savedRecipeRepository.findByUserIdOrderBySavedAtDesc(userId);
            
            // Convert to response format
            List<Map<String, Object>> response = recipes.stream()
                    .map(r -> {
                        try {
                            Map<String, Object> recipeMap = objectMapper.readValue(r.getRecipeJson(), Map.class);
                            recipeMap.put("savedId", r.getId());
                            recipeMap.put("savedAt", r.getSavedAt().toString());
                            return recipeMap;
                        } catch (Exception e) {
                            return Map.of("error", "Failed to parse recipe");
                        }
                    })
                    .toList();
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
    
    @DeleteMapping("/saved/{id}")
    public ResponseEntity<?> deleteSavedRecipe(@PathVariable Long id, @RequestParam Long userId) {
        try {
            savedRecipeRepository.deleteByIdAndUserId(id, userId);
            return ResponseEntity.ok(Map.of("message", "Recipe deleted successfully"));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
}
