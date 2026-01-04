package com.ai.SpringAIProject.service;

import com.ai.SpringAIProject.model.User;
import com.ai.SpringAIProject.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public User register(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        return userRepository.save(user);
    }

    public User login(String username, String password) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            if (passwordEncoder.matches(password, user.getPassword())) {
                return user;
            }
        }
        return null;
    }
    
    public User updateUserProfile(Long userId, User updatedData) {
        User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("User not found"));
        user.setWeightKg(updatedData.getWeightKg());
        user.setHeightCm(updatedData.getHeightCm());
        user.setAge(updatedData.getAge());
        user.setGender(updatedData.getGender());
        user.setActivityLevel(updatedData.getActivityLevel());
        user.setHealthGoals(updatedData.getHealthGoals());
        user.setDietaryRestrictions(updatedData.getDietaryRestrictions());
        return userRepository.save(user);
    }
}
