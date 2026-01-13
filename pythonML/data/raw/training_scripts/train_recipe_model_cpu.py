"""
Recipe Model Training Script (CPU-Optimized)
Trains DistilGPT2 on recipe data using Intel Core Ultra 125H
Optimized for 16GB RAM, 8-10 hour training time
"""

import os
from pathlib import Path
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    GPT2Config,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)
import torch

def main():
    print("="*70)
    print("Recipe Model Training (CPU-Optimized for 16GB RAM)")
    print("="*70)
    
    # Check if data file exists
    data_file = 'data/recipe_training.txt'
    if not Path(data_file).exists():
        print(f"❌ Error: {data_file} not found!")
        print("Please run prepare_recipe_data.py first")
        return
    
    print(f"\n📊 Training Configuration:")
    print(f"   Model: DistilGPT2 (82M parameters)")
    print(f"   Data file: {data_file}")
    print(f"   File size: {Path(data_file).stat().st_size / (1024*1024):.2f} MB")
    print(f"   Device: CPU (Intel Core Ultra 125H)")
    print(f"   Batch size: 2 (optimized for 16GB RAM)")
    print(f"   Estimated time: 8-10 hours")
    print(f"   Checkpoints: Saved every 1000 steps (~30 min)")
    
    # Initialize tokenizer
    print("\n🔧 Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
    tokenizer.pad_token = tokenizer.eos_token
    
    # Initialize model
    print("🔧 Loading DistilGPT2 model...")
    model = GPT2LMHeadModel.from_pretrained('distilgpt2')
    
    # Enable gradient checkpointing to save memory
    model.gradient_checkpointing_enable()
    
    print(f"   Model parameters: {model.num_parameters():,}")
    
    # Prepare dataset
    print("\n📚 Preparing training dataset...")
    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=data_file,
        block_size=128  # Shorter sequences to save memory
    )
    
    print(f"   Training samples: {len(train_dataset)}")
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Create output directory
    output_dir = 'app/models/recipe_gpt2'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Training arguments (CPU-optimized for 16GB RAM)
    print("\n⚙️  Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Small batch for 16GB RAM
        gradient_accumulation_steps=8,  # Effective batch size = 2 * 8 = 16
        save_steps=1000,  # Save every ~30 minutes
        save_total_limit=3,  # Keep only last 3 checkpoints
        logging_steps=100,
        logging_dir=f'{output_dir}/logs',
        no_cuda=True,  # Force CPU training
        dataloader_num_workers=4,  # Use 4 CPU cores for data loading
        fp16=False,  # Disable mixed precision (not supported on CPU)
        learning_rate=5e-5,
        warmup_steps=500,
        weight_decay=0.01,
        logging_first_step=True,
        prediction_loss_only=True,
    )
    
    # Initialize trainer
    print("\n🚀 Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    
    # Start training
    print("\n" + "="*70)
    print("🔥 STARTING TRAINING")
    print("="*70)
    print("⏰ Estimated completion: 8-10 hours")
    print("💡 Tip: Start this before bed and check in the morning!")
    print("📊 Progress will be logged every 100 steps")
    print("💾 Checkpoints saved every 1000 steps to:", output_dir)
    print("="*70 + "\n")
    
    try:
        trainer.train()
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETE!")
        print("="*70)
        
        # Save final model
        print("\n💾 Saving final model and tokenizer...")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        print(f"\n📁 Model saved to: {output_dir}")
        print("\n✅ Training pipeline completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Test the model with: python test_recipe_generation.py")
        print("   2. Integrate into ml_service.py")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("💾 Latest checkpoint saved, you can resume training later")
    except Exception as e:
        print(f"\n\n❌ Training failed with error: {e}")
        print("💾 Check if latest checkpoint was saved")

if __name__ == "__main__":
    main()
