package com.ai.SpringAIProject.controller;

import com.ai.SpringAIProject.service.MLBridgeService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@CrossOrigin(originPatterns = "*")
public class ChatController {

    private final MLBridgeService mlService;

    public ChatController(MLBridgeService mlService) {
        this.mlService = mlService;
    }

    @PostMapping
    public Object chat(@RequestParam String message) {
        System.out.println("Chat message received: " + message);
        return mlService.chat(message);
    }
}
