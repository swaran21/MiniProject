package com.ai.SpringAIProject.security;

import com.ai.SpringAIProject.dto.LoginRequest;
import com.ai.SpringAIProject.dto.LoginResponse;
import com.ai.SpringAIProject.dto.RegisterRequest;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.*;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Integration tests for JWT Authentication
 * Verifies the complete authentication flow:
 * 1. User Registration
 * 2. Login & Token Generation
 * 3. Accessing Protected Endpoints
 * 4. Token Refresh
 * 5. Security & Unauthorized Access Handling
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@AutoConfigureMockMvc
@ActiveProfiles("test")
class JwtAuthenticationIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private MockMvc mockMvc;

    private String baseUrl;
    private static String accessToken;
    private static String refreshToken;
    private static Long userId;

    @BeforeEach
    void setUp() {
        baseUrl = "http://localhost:" + port;
    }

    @Test
    @Order(1)
    @DisplayName("1. Should successfully register a new user")
    void testUserRegistration() {
        // Arrange
        RegisterRequest request = new RegisterRequest();
        request.setUsername("testuser_" + Instant.now().toEpochMilli());
        request.setPassword("Test123!");
        request.setAge(30);
        request.setGender("M");
        request.setWeightKg(75.0);
        request.setHeightCm(175.0);
        request.setActivityLevel("Moderate");
        request.setHealthGoals("Balanced");

        // Act
        ResponseEntity<LoginResponse> response = restTemplate.postForEntity(
                baseUrl + "/api/auth/register",
                request,
                LoginResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getAccessToken()).isNotBlank();
        assertThat(response.getBody().getRefreshToken()).isNotBlank();
        assertThat(response.getBody().getTokenType()).isEqualTo("Bearer");
        assertThat(response.getBody().getUserId()).isNotNull();
        assertThat(response.getBody().getRoles()).contains("USER");

        // Store artifacts for subsequent tests
        accessToken = response.getBody().getAccessToken();
        refreshToken = response.getBody().getRefreshToken();
        userId = response.getBody().getUserId();
    }

    @Test
    @Order(2)
    @DisplayName("2. Should successfully login with valid credentials")
    void testUserLogin() {
        // Arrange - Create a fresh user for login test
        String username = "logintest_" + Instant.now().toEpochMilli();
        populateUser(username, "Test123!");

        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername(username);
        loginRequest.setPassword("Test123!");

        // Act
        ResponseEntity<LoginResponse> response = restTemplate.postForEntity(
                baseUrl + "/api/auth/login",
                loginRequest,
                LoginResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getAccessToken()).isNotBlank();
        assertThat(response.getBody().getRefreshToken()).isNotBlank();
    }

    @Test
    @Order(3)
    void testInvalidLogin() throws Exception {
        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                {
                  "username": "nonexistent_user",
                  "password": "wrongpassword"
                }
            """))
                .andExpect(status().isUnauthorized());
    }



    private LoginResponse registerAndLogin() {
        // 1. Create unique username
        String username = "testuser_" + Instant.now().toEpochMilli();

        // 2. Build register request
        RegisterRequest request = new RegisterRequest();
        request.setUsername(username);
        request.setPassword("Test123!");
        request.setAge(25);
        request.setGender("M");
        request.setWeightKg(70.0);
        request.setHeightCm(170.0);
        request.setActivityLevel("Moderate");
        request.setHealthGoals("Balanced");

        // 3. Call register endpoint
        ResponseEntity<LoginResponse> response =
                restTemplate.postForEntity(
                        baseUrl + "/api/auth/register",
                        request,
                        LoginResponse.class
                );

        // 4. Validate response early (fail fast)
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getAccessToken()).isNotBlank();
        assertThat(response.getBody().getUserId()).isNotNull();

        // 5. Return tokens
        return response.getBody();
    }


    @Test
    @Order(5)
    @DisplayName("5. Should deny access to protected endpoint without token")
    void testProtectedEndpointWithoutToken() {
        // Act
        ResponseEntity<String> response = restTemplate.getForEntity(
                baseUrl + "/api/health/meal-plan/" + userId + "/active",
                String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isIn(HttpStatus.UNAUTHORIZED, HttpStatus.FORBIDDEN);
    }

    @Test
    @Order(6)
    @DisplayName("6. Should deny access with invalid token")
    void testProtectedEndpointWithInvalidToken() {
        // Arrange
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("INVALID_TOKEN_SIGNATURE");
        HttpEntity<String> entity = new HttpEntity<>(headers);

        // Act
        ResponseEntity<String> response = restTemplate.exchange(
                baseUrl + "/api/health/meal-plan/" + userId + "/active",
                HttpMethod.GET,
                entity,
                String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isIn(HttpStatus.UNAUTHORIZED, HttpStatus.FORBIDDEN);
    }

    @Test
    @Order(7)
    @DisplayName("7. Should refresh access token using valid refresh token")
    void testTokenRefresh() {
        // Arrange
        Map<String, String> requestBody = new HashMap<>();
        requestBody.put("refreshToken", refreshToken);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(requestBody, headers);

        // Act
        ResponseEntity<String> response = restTemplate.postForEntity(
                baseUrl + "/api/auth/refresh",
                entity,
                String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("accessToken");
    }

    @Test
    @Order(8)
    @DisplayName("8. Should allow access to public endpoints without authentication")
    void testPublicEndpoints() {
        // Act
        ResponseEntity<String> healthResponse = restTemplate.getForEntity(
                baseUrl + "/health",
                String.class
        );

        ResponseEntity<String> rootResponse = restTemplate.getForEntity(
                baseUrl + "/",
                String.class
        );

        // Assert
        assertThat(healthResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(rootResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    // Helper method to create a user for tests
    private void populateUser(String username, String password) {
        RegisterRequest request = new RegisterRequest();
        request.setUsername(username);
        request.setPassword(password);
        request.setAge(25);
        request.setWeightKg(70.0);
        request.setHeightCm(170.0);
        
        restTemplate.postForEntity(
                baseUrl + "/api/auth/register",
                request,
                LoginResponse.class
        );
    }
}
