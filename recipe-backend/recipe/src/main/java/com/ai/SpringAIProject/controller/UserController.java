package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*") // Allow frontend access
public class UserController {

    private final UserRepository userRepository;

    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Get user profile by ID
     * Accessible by: The user themselves or ADMIN
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getUserProfile(@PathVariable Long id) {
        try {
            // 1. Get currently authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String currentUsername = authentication.getName();
            
            // 2. Fetch target user
            User user = userRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("User not found"));

            // 3. Security Check: Allow if admin or same user
            boolean isAdmin = authentication.getAuthorities().stream()
                    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
            
            if (!user.getUsername().equals(currentUsername) && !isAdmin) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("error", "Access denied: You can only view your own profile"));
            }

            // 4. Return user data (DTO or entity with password ignored via JsonIgnore if configured, 
            //    but safe to map manually or just rely on lombok if password field isn't hidden. 
            //    For now returning entity but we should be careful about password. 
            //    Best practice: Use DTO. For speed: manually map map.)
            
            // Let's return a Map to be safe and avoid leaking password
            return ResponseEntity.ok(Map.of(
                "id", user.getId(),
                "username", user.getUsername(),
                "roles", user.getRoles(),
                "age", user.getAge() != null ? user.getAge() : 0,
                "weightKg", user.getWeightKg() != null ? user.getWeightKg() : 0.0,
                "heightCm", user.getHeightCm() != null ? user.getHeightCm() : 0.0,
                "gender", user.getGender() != null ? user.getGender() : "N/A",
                "activityLevel", user.getActivityLevel() != null ? user.getActivityLevel() : "Moderate",
                "healthGoals", user.getHealthGoals() != null ? user.getHealthGoals() : "Balanced",
                "dietaryRestrictions", user.getDietaryRestrictions() != null ? user.getDietaryRestrictions() : "None"
            ));

        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error fetching profile"));
        }
    }
}
