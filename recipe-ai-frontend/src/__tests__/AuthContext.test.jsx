import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { vi, describe, it, expect } from 'vitest';
import React from 'react';

// Mock the AuthContext hook just for components that consume it
// But here we want to test the Provider itself, so we need to mock fetch/api
global.fetch = vi.fn();

// Test Component to consume context
const TestComponent = () => {
    const { user, login, logout, isAuthenticated } = useAuth();
    return (
        <div>
            <div data-testid="auth-status">{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>
            <div data-testid="user-name">{user?.username}</div>
            <button onClick={() => login('testuser', 'password')}>Login</button>
            <button onClick={logout}>Logout</button>
        </div>
    );
};

describe('AuthContext', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it('provides initial state as not authenticated', () => {
        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });

    it('loads user from localStorage on mount', async () => {
        // Arrange
        localStorage.setItem('accessToken', 'test-token');
        localStorage.setItem('user', JSON.stringify({ username: 'storedUser' }));

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        // Assert
        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
            expect(screen.getByTestId('user-name')).toHaveTextContent('storedUser');
        });
    });

    it('login function updates state on success', async () => {
        // Mock successful API response
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                accessToken: 'new-token',
                refreshToken: 'refresh-token',
                userId: 1,
                username: 'testuser',
                roles: 'USER'
            })
        });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        // Act
        screen.getByText('Login').click();

        // Assert
        await waitFor(() => {
            expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
            expect(screen.getByTestId('user-name')).toHaveTextContent('testuser');
        });
        expect(localStorage.getItem('accessToken')).toBe('new-token');
    });

    it('logout function clears state and storage', async () => {
        // Arrange - set initial logged in state
        localStorage.setItem('accessToken', 'token');
        localStorage.setItem('user', JSON.stringify({ username: 'user' }));

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        // Wait for initial load
        await waitFor(() => expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated'));

        // Act
        screen.getByText('Logout').click();

        // Assert
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
        expect(localStorage.getItem('accessToken')).toBeNull();
    });
});
