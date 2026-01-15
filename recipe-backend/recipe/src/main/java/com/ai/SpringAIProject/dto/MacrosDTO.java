package com.ai.SpringAIProject.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for macronutrient breakdown
 * 
 * Provides structured access to protein, carbs, and fats
 * for UI components (charts, progress bars, etc.)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MacrosDTO {
    
    private Integer protein;  // grams
    private Integer carbs;    // grams
    private Integer fats;     // grams
    
    /**
     * Utility: Convert to display string "P:20 C:40 F:15"
     */
    public String toDisplayString() {
        return String.format("P:%d C:%d F:%d", protein, carbs, fats);
    }
    
    /**
     * Utility: Calculate total calories
     * Protein: 4 cal/g, Carbs: 4 cal/g, Fats: 9 cal/g
     */
    public int calculateCalories() {
        return (protein * 4) + (carbs * 4) + (fats * 9);
    }
    
    /**
     * Factory: Parse from string "P:20 C:40 F:15"
     */
    public static MacrosDTO fromString(String macros) {
        if (macros == null || macros.isEmpty()) {
            return new MacrosDTO(0, 0, 0);
        }
        
        int protein = 0, carbs = 0, fats = 0;
        
        try {
            for (String part : macros.split("\\s+")) {
                if (part.startsWith("P:")) protein = Integer.parseInt(part.substring(2));
                else if (part.startsWith("C:")) carbs = Integer.parseInt(part.substring(2));
                else if (part.startsWith("F:")) fats = Integer.parseInt(part.substring(2));
            }
        } catch (Exception e) {
            System.err.println("Error parsing macros: " + macros);
        }
        
        return new MacrosDTO(protein, carbs, fats);
    }
}
