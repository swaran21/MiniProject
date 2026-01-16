import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginComponent from '../components/LoginComponent';
import { useAuth } from '../context/AuthContext';
import { vi, describe, it, expect } from 'vitest';
import React from 'react';

// Mock the useAuth hook
vi.mock('../context/AuthContext', () => ({
    useAuth: vi.fn(),
}));

describe('LoginComponent', () => {
    const mockLogin = vi.fn();
    const mockRegister = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
        // Default mock return
        useAuth.mockReturnValue({
            login: mockLogin,
            register: mockRegister,
        });
    });

    it('renders login form by default', () => {
        render(<LoginComponent />);
        expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
    });

    it('switches to registration mode', () => {
        render(<LoginComponent />);
        
        // Find toggle button (span with "Register" text)
        const toggleButton = screen.getByText('Register');
        fireEvent.click(toggleButton);

        // Should now show registration fields like Age/Gender
        expect(screen.getByPlaceholderText('25')).toBeInTheDocument(); // Age field
    });

    it('calls login function with credentials', async () => {
        // Mock successful login
        mockLogin.mockResolvedValue({ success: true });

        render(<LoginComponent />);

        // Fill form
        fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'testuser' } });
        fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'password123' } });

        // Submit
        fireEvent.click(screen.getByRole('button', { name: /Login/i }));

        // Assert
        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123');
        });
    });

    it('displays error message on failed login', async () => {
        // Mock failed login
        mockLogin.mockResolvedValue({ success: false, error: 'Invalid credentials' });

        render(<LoginComponent />);

        // Use change/click via fireEvent is fine, but ensure we await state updates if needed
        // Or better, just wait for the error message
        fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'testuser' } });
        fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'password123' } });
        
        fireEvent.click(screen.getByRole('button', { name: /Login/i }));

        await waitFor(() => {
            expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
        });
    });
});
