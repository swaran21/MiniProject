package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.dto.LoginRequest;
import com.ai.SpringAIProject.dto.LoginResponse;
import com.ai.SpringAIProject.dto.RegisterRequest;
import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;
import com.ai.SpringAIProject.security.JwtTokenProvider;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Authentication Controller
 * Handles user registration, login, and token refresh
 */
@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuthenticationManager authenticationManager;

    public AuthController(UserRepository userRepository, 
                         PasswordEncoder passwordEncoder,
                         JwtTokenProvider jwtTokenProvider,
                         AuthenticationManager authenticationManager) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenProvider = jwtTokenProvider;
        this.authenticationManager = authenticationManager;
    }

    /**
     * POST /api/auth/register
     * Register a new user
     */
    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest request) {
        try {
            // Check if username already exists
            if (userRepository.findByUsername(request.getUsername()).isPresent()) {
                return ResponseEntity.status(HttpStatus.CONFLICT)
                        .body(Map.of("error", "Username already exists"));
            }

            // Create new user
            User user = new User();
            user.setUsername(request.getUsername());
            user.setPassword(passwordEncoder.encode(request.getPassword()));
            
            // Set profile data
            user.setWeightKg(request.getWeightKg());
            user.setHeightCm(request.getHeightCm());
            user.setAge(request.getAge());
            user.setGender(request.getGender());
            user.setActivityLevel(request.getActivityLevel());
            user.setHealthGoals(request.getHealthGoals());
            user.setDietaryRestrictions(request.getDietaryRestrictions());

            User savedUser = userRepository.save(user);

            // Generate tokens
            String accessToken = jwtTokenProvider.generateAccessToken(savedUser.getUsername(), savedUser.getRoles());
            String refreshToken = jwtTokenProvider.generateRefreshToken(savedUser.getUsername());

            LoginResponse response = LoginResponse.builder()
                    .accessToken(accessToken)
                    .refreshToken(refreshToken)
                    .tokenType("Bearer")
                    .userId(savedUser.getId())
                    .username(savedUser.getUsername())
                    .roles(savedUser.getRoles())
                    .expiresIn(900000) // 15 minutes
                    .build();

            return ResponseEntity.status(HttpStatus.CREATED).body(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Registration failed: " + e.getMessage()));
        }
    }

    /**
     * POST /api/auth/login
     * Authenticate user and return JWT tokens
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        try {
            // Authenticate user
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            request.getUsername(),
                            request.getPassword()
                    )
            );

            // Get user from database
            User user = userRepository.findByUsername(request.getUsername())
                    .orElseThrow(() -> new RuntimeException("User not found"));

            // Generate tokens
            String accessToken = jwtTokenProvider.generateAccessToken(user.getUsername(), user.getRoles());
            String refreshToken = jwtTokenProvider.generateRefreshToken(user.getUsername());

            LoginResponse response = LoginResponse.builder()
                    .accessToken(accessToken)
                    .refreshToken(refreshToken)
                    .tokenType("Bearer")
                    .userId(user.getId())
                    .username(user.getUsername())
                    .roles(user.getRoles())
                    .expiresIn(900000) // 15 minutes
                    .build();

            return ResponseEntity.ok(response);

        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid credentials"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Login failed: " + e.getMessage()));
        }
    }

    /**
     * POST /api/auth/refresh
     * Refresh access token using refresh token
     */
    @PostMapping("/refresh")
    public ResponseEntity<?> refresh(@RequestBody Map<String, String> request) {
        try {
            String refreshToken = request.get("refreshToken");
            
            if (refreshToken == null || !jwtTokenProvider.validateToken(refreshToken)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid refresh token"));
            }

            String username = jwtTokenProvider.getUsernameFromToken(refreshToken);
            User user = userRepository.findByUsername(username)
                    .orElseThrow(() -> new RuntimeException("User not found"));

            // Generate new access token
            String newAccessToken = jwtTokenProvider.generateAccessToken(user.getUsername(), user.getRoles());

            Map<String, Object> response = new HashMap<>();
            response.put("accessToken", newAccessToken);
            response.put("tokenType", "Bearer");
            response.put("expiresIn", 900000);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Token refresh failed: " + e.getMessage()));
        }
    }
}
