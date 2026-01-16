package com.ai.SpringAIProject.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import javax.crypto.SecretKey;
import java.util.Date;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertTrue;

@ExtendWith(MockitoExtension.class)
class JwtTokenProviderTest {

    @InjectMocks
    private JwtTokenProvider jwtTokenProvider;

    private final String secret = "404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970";
    private final long jwtExpiration = 3600000; // 1 hour
    private final long refreshExpiration = 7200000; // 2 hours

    @BeforeEach
    void setUp() {
        // Manually inject values since we are running a unit test without Spring context
        ReflectionTestUtils.setField(jwtTokenProvider, "jwtSecret", secret);
        ReflectionTestUtils.setField(jwtTokenProvider, "accessTokenExpiration", jwtExpiration);
        ReflectionTestUtils.setField(jwtTokenProvider, "refreshTokenExpiration", refreshExpiration);
        // jwtTokenProvider.init(); // Initialize the key - method removed as key is generated on demand
    }

    @Test
    @DisplayName("Should generate valid access token")
    void generateToken() {
        // Arrange
        String username = "testuser";
        String roles = "USER";

        // Act
        String token = jwtTokenProvider.generateAccessToken(username, roles);

        // Assert
        assertThat(token).isNotNull().isNotEmpty();
        assertTrue(jwtTokenProvider.validateToken(token));
        assertThat(jwtTokenProvider.getUsernameFromToken(token)).isEqualTo("testuser");
    }

    @Test
    @DisplayName("Should generate valid refresh token")
    void generateRefreshToken() {
        // Arrange
        String username = "testuser";

        // Act
        String refreshToken = jwtTokenProvider.generateRefreshToken(username);

        // Assert
        assertThat(refreshToken).isNotNull().isNotEmpty();
        assertTrue(jwtTokenProvider.validateToken(refreshToken));
        assertThat(jwtTokenProvider.getUsernameFromToken(refreshToken)).isEqualTo("testuser");
    }

    @Test
    @DisplayName("Should validate correct token")
    void validateToken() {
        // Arrange
        String username = "testuser";
        String roles = "USER";
        String token = jwtTokenProvider.generateAccessToken(username, roles);

        // Act & Assert
        assertTrue(jwtTokenProvider.validateToken(token));
    }

    @Test
    @DisplayName("Should invalidate expired token")
    void validateExpiredToken() {
        // Arrange - Create a token that expired in the past
        Date now = new Date();
        Date pastDate = new Date(now.getTime() - 10000);
        SecretKey key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));

        String expiredToken = Jwts.builder()
                .subject("testuser")
                .issuedAt(new Date(now.getTime() - 20000))
                .expiration(pastDate)
                .signWith(key)
                .compact();

        // Act & Assert
        // Note: validateToken logs exception and returns false
        assertThat(jwtTokenProvider.validateToken(expiredToken)).isFalse();
    }
}
