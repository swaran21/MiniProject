package com.ai.SpringAIProject.security;

import com.ai.SpringAIProject.dto.LoginRequest;
import com.ai.SpringAIProject.dto.LoginResponse;
import com.ai.SpringAIProject.dto.RegisterRequest;
import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.*;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration tests for JWT Authentication
 * Tests the complete authentication flow from registration to protected endpoint access
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@ActiveProfiles("test")
class JwtAuthenticationIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private UserRepository userRepository;

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
    @DisplayName("1. Should register new user and return JWT tokens")
    void testUserRegistration() {
        // Arrange
        RegisterRequest request = new RegisterRequest();
        request.setUsername("testuser_" + System.currentTimeMillis());
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

        // Save for next tests
        accessToken = response.getBody().getAccessToken();
        refreshToken = response.getBody().getRefreshToken();
        userId = response.getBody().getUserId();

        System.out.println("✅ Registration successful. Access Token: " + accessToken.substring(0, 20) + "...");
    }

    @Test
    @Order(2)
    @DisplayName("2. Should login with valid credentials")
    void testUserLogin() {
        // First, create a user
        String username = "logintest_" + System.currentTimeMillis();
        RegisterRequest registerRequest = new RegisterRequest();
        registerRequest.setUsername(username);
        registerRequest.setPassword("Test123!");
        registerRequest.setAge(25);

        restTemplate.postForEntity(
                baseUrl + "/api/auth/register",
                registerRequest,
                LoginResponse.class
        );

        // Arrange
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

        System.out.println("✅ Login successful");
    }

    @Test
    @Order(3)
    @DisplayName("3. Should reject login with invalid credentials")
    void testInvalidLogin() {
        // Arrange
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("nonexistent");
        loginRequest.setPassword("wrongpassword");

        // Act
        ResponseEntity<String> response = restTemplate.postForEntity(
                baseUrl + "/api/auth/login",
                loginRequest,
                String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);

        System.out.println("✅ Invalid login rejected");
    }

    @Test
    @Order(4)
    @DisplayName("4. Should access protected endpoint with valid token")
    void testProtectedEndpointWithToken() {
        // Arrange
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        // Act
        ResponseEntity<String> response = restTemplate.exchange(
                baseUrl + "/api/health/meal-plan/" + userId + "/active",
                HttpMethod.GET,
                entity,
                String.class
        );

        // Assert - Should be authenticated (200 or 404, not 401/403)
        assertThat(response.getStatusCode()).isNotEqualTo(HttpStatus.UNAUTHORIZED);
        assertThat(response.getStatusCode()).isNotEqualTo(HttpStatus.FORBIDDEN);

        System.out.println("✅ Protected endpoint accessible with token. Status: " + response.getStatusCode());
    }

    @Test
    @Order(5)
    @DisplayName("5. Should reject access to protected endpoint without token")
    void testProtectedEndpointWithoutToken() {
        // Act
        ResponseEntity<String> response = restTemplate.getForEntity(
                baseUrl + "/api/health/meal-plan/" + userId + "/active",
                String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isIn(HttpStatus.UNAUTHORIZED, HttpStatus.FORBIDDEN);

        System.out.println("✅ Protected endpoint blocked without token. Status: " + response.getStatusCode());
    }

    @Test
    @Order(6)
    @DisplayName("6. Should reject access with invalid token")
    void testProtectedEndpointWithInvalidToken() {
        // Arrange
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("INVALID_TOKEN_123");
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

        System.out.println("✅ Invalid token rejected");
    }

    @Test
    @Order(7)
    @DisplayName("7. Should refresh access token using refresh token")
    void testTokenRefresh() {
        // Arrange
        String requestBody = "{\"refreshToken\": \"" + refreshToken + "\"}";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);

        // Act
        ResponseEntity<String> response = restTemplate.postForEntity(
                baseUrl + "/api/auth/refresh",
                entity,
                String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("accessToken");

        System.out.println("✅ Token refresh successful");
    }

    @Test
    @Order(8)
    @DisplayName("8. Should access public endpoints without token")
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

        System.out.println("✅ Public endpoints accessible without token");
    }

    @AfterAll
    static void cleanup() {
        System.out.println("\n📊 JWT Authentication Tests Complete!");
        System.out.println("All security features verified ✅");
    }
}
