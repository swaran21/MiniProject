"""
Test Recipe Generation Script
Tests the trained GPT-2 model with sample ingredients
"""

from transformers import GPT2LMHeadModel, GPT2Tokenizer
from pathlib import Path

def generate_recipe(model, tokenizer, ingredients, max_length=400):
    """Generate a recipe from simple ingredient list"""
    # Format input
    input_text = f"INPUT: {ingredients}\nOUTPUT:"
    
    # Tokenize
    inputs = tokenizer(input_text, return_tensors='pt')
    
    # Generate
    outputs = model.generate(
        inputs['input_ids'],
        max_length=max_length,
        num_return_sequences=1,
        temperature=0.8,  # Some randomness for creativity
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.encode('<END>')[0] if '<END>' in tokenizer.get_vocab() else tokenizer.eos_token_id
    )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract OUTPUT section
    if 'OUTPUT:' in generated_text:
        recipe = generated_text.split('OUTPUT:')[1].strip()
        if '<END>' in recipe:
            recipe = recipe.split('<END>')[0].strip()
        return recipe
    
    return generated_text

def main():
    print("="*70)
    print("Recipe Generation Test")
    print("="*70)
    
    # Check if model exists
    model_dir = 'app/models/recipe_gpt2'
    if not Path(model_dir).exists():
        print(f"\n❌ Error: Model not found at {model_dir}")
        print("Please run train_recipe_model_cpu.py first")
        return
    
    # Load model and tokenizer
    print(f"\n🔧 Loading model from {model_dir}...")
    tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
    model = GPT2LMHeadModel.from_pretrained(model_dir)
    model.eval()  # Set to evaluation mode
    
    print("✅ Model loaded successfully!\n")
    
    # Test cases
    test_ingredients = [
        "tomato, onions, chicken",
        "pasta, garlic, olive oil, basil",
        "eggs, milk, flour, sugar",
        "rice, soy sauce, vegetables",
        "potato, cheese, bacon"
    ]
    
    print("="*70)
    print("🧪 Running test cases...")
    print("="*70)
    
    for i, ingredients in enumerate(test_ingredients, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {ingredients}")
        print("="*70)
        
        try:
            recipe = generate_recipe(model, tokenizer, ingredients)
            print(recipe)
        except Exception as e:
            print(f"❌ Error generating recipe: {e}")
    
    # Interactive mode
    print("\n" + "="*70)
    print("🎮 Interactive Mode - Enter your own ingredients!")
    print("   (Type 'quit' to exit)")
    print("="*70)
    
    while True:
        user_input = input("\n🥘 Enter ingredients (comma-separated): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            print("\n🔮 Generating recipe...\n")
            recipe = generate_recipe(model, tokenizer, user_input)
            print("="*70)
            print(recipe)
            print("="*70)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
