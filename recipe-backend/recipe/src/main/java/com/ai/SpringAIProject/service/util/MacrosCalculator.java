package com.ai.SpringAIProject.service.util;

import org.springframework.stereotype.Component;

/**
 * Utility class for all macronutrient calculations and parsing
 * 
 * SINGLE RESPONSIBILITY: Macros manipulation only
 * 
 * Handles:
 * - Parsing macros strings ("P:20 C:40 F:15")
 * - Estimating macros from calories
 * - Summing macros from multiple meals
 * - Converting between formats
 */
@Component
public class MacrosCalculator {
    
    /**
     * Parse macros string "P:20 C:40 F:15" into array [protein, carbs, fats]
     */
    public int[] parseMacrosString(String macros) {
        int[] result = new int[3]; // [protein, carbs, fats]
        
        if (macros == null || macros.isEmpty()) {
            return result;
        }
        
        try {
            for (String part : macros.split("\\s+")) {
                if (part.startsWith("P:")) {
                    result[0] = Integer.parseInt(part.substring(2));
                } else if (part.startsWith("C:")) {
                    result[1] = Integer.parseInt(part.substring(2));
                } else if (part.startsWith("F:")) {
                    result[2] = Integer.parseInt(part.substring(2));
                }
            }
        } catch (Exception e) {
            System.err.println("Error parsing macros: " + macros);
        }
        
        return result;
    }
    
    /**
     * Format macros array [20, 40, 15] into string "P:20 C:40 F:15"
     */
    public String formatMacros(int protein, int carbs, int fats) {
        return String.format("P:%d C:%d F:%d", protein, carbs, fats);
    }
    
    /**
     * Estimate macros from calories using standard healthy ratios
     * 
     * Ratios: 30% protein, 40% carbs, 30% fats (by calories)
     * Conversion: Protein 4 cal/g, Carbs 4 cal/g, Fats 9 cal/g
     */
    public String estimateMacrosFromCalories(int calories) {
        int protein = (int) Math.round((calories * 0.30) / 4.0);  // 30% calories, 4 cal/g
        int carbs = (int) Math.round((calories * 0.40) / 4.0);    // 40% calories, 4 cal/g
        int fats = (int) Math.round((calories * 0.30) / 9.0);     // 30% calories, 9 cal/g
        return formatMacros(protein, carbs, fats);
    }
    
    /**
     * Sum macros from multiple meals
     * 
     * @param macrosList List of macros strings ["P:20 C:40 F:15", "P:30 C:50 F:20", ...]
     * @return Summed macros string "P:50 C:90 F:35"
     */
    public String sumMacros(String... macrosList) {
        int totalProtein = 0;
        int totalCarbs = 0;
        int totalFats = 0;
        
        for (String macros : macrosList) {
            if (macros != null && !macros.isEmpty()) {
                int[] parsed = parseMacrosString(macros);
                totalProtein += parsed[0];
                totalCarbs += parsed[1];
                totalFats += parsed[2];
            }
        }
        
        return formatMacros(totalProtein, totalCarbs, totalFats);
    }
    
    /**
     * Calculate total calories from macros
     * Protein: 4 cal/g, Carbs: 4 cal/g, Fats: 9 cal/g
     */
    public int calculateCaloriesFromMacros(String macros) {
        int[] parsed = parseMacrosString(macros);
        return (parsed[0] * 4) + (parsed[1] * 4) + (parsed[2] * 9);
    }
    
    /**
     * Validate macros string format
     */
    public boolean isValidMacrosFormat(String macros) {
        return macros != null && macros.matches("P:\\d+ C:\\d+ F:\\d+");
    }
}
