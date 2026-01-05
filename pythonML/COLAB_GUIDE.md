# Google Colab GPU Training - Quick Guide

## Setup (5 minutes)
1. Go to https://colab.research.google.com
2. Upload `Recipe_GPT2_Training.ipynb`
3. Runtime → Change runtime → GPU
4. Upload files:
   - `recipe_gpt2_light.zip` (your model)
   - `recipe_training_combined.txt` (training data)

## Training (1-2 hours on GPU)
- Run all cells
- Wait for completion
- Download `recipe_gpt2_final.zip`

## After Training
1. Extract to `pythonML/app/models/recipe_gpt2/`
2. Restart Python backend
3. Test improved recipes!

**Result:** Much better recipe quality for all cuisines including Korean, Mediterranean, Indian, Japanese!
