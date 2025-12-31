"""
Recipe Model Training Script (GPU-Optimized)
Trains DistilGPT2 on recipe data using NVIDIA RTX 3050
Optimized for 4GB VRAM, ~2-3 hour training time (vs 22 hours on CPU)
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
    print("Recipe Model Training (GPU-Optimized for RTX 3050)")
    print("="*70)
    
    # Check GPU availability
    if not torch.cuda.is_available():
        print("\n⚠️  WARNING: No GPU detected!")
        print("This script is optimized for GPU. For CPU training, use train_recipe_model_cpu.py")
        response = input("\nContinue with CPU anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print(f"\n✅ GPU Detected: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Check if data file exists
    data_file = 'data/recipe_training.txt'
    if not Path(data_file).exists():
        print(f"\n❌ Error: {data_file} not found!")
        print("Please run prepare_recipe_data.py first")
        return
    
    print(f"\n📊 Training Configuration:")
    print(f"   Model: DistilGPT2 (82M parameters)")
    print(f"   Data file: {data_file}")
    print(f"   File size: {Path(data_file).stat().st_size / (1024*1024):.2f} MB")
    print(f"   Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
    print(f"   Batch size: 8 (GPU-optimized)")
    print(f"   Estimated time: 2-3 hours with RTX 3050")
    print(f"   Checkpoints: Saved every 500 steps (~15 min)")
    
    # Initialize tokenizer
    print("\n🔧 Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
    tokenizer.pad_token = tokenizer.eos_token
    
    # Initialize model
    print("🔧 Loading DistilGPT2 model...")
    model = GPT2LMHeadModel.from_pretrained('distilgpt2')
    
    # Move to GPU if available
    if torch.cuda.is_available():
        model = model.to('cuda')
        print("   Model moved to GPU ✅")
    
    print(f"   Model parameters: {model.num_parameters():,}")
    
    # Prepare dataset
    print("\n📚 Preparing training dataset...")
    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=data_file,
        block_size=128
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
    
    # Training arguments (GPU-optimized)
    print("\n⚙️  Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=8,  # GPU can handle larger batches
        gradient_accumulation_steps=2,  # Effective batch size = 8 * 2 = 16
        save_steps=500,  # Save every ~15 minutes on GPU
        save_total_limit=3,
        logging_steps=50,  # More frequent logging on GPU
        logging_dir=f'{output_dir}/logs',
        fp16=torch.cuda.is_available(),  # Mixed precision for faster training
        dataloader_num_workers=4,
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
    
    # Check for existing checkpoints
    checkpoints = list(Path(output_dir).glob('checkpoint-*'))
    if checkpoints:
        latest_checkpoint = max(checkpoints, key=lambda p: int(p.name.split('-')[1]))
        print(f"\n📂 Found existing checkpoint: {latest_checkpoint.name}")
        resume = input("   Resume from this checkpoint? (y/n): ")
        if resume.lower() == 'y':
            print(f"\n🔄 Resuming from {latest_checkpoint.name}")
            resume_from_checkpoint = str(latest_checkpoint)
        else:
            resume_from_checkpoint = None
    else:
        resume_from_checkpoint = None
    
    # Start training
    print("\n" + "="*70)
    print("🔥 STARTING TRAINING")
    print("="*70)
    if torch.cuda.is_available():
        print("⚡ GPU Training Mode")
        print("⏰ Estimated completion: 2-3 hours")
    else:
        print("🐌 CPU Training Mode")
        print("⏰ Estimated completion: 8-10 hours")
    print("💡 Tip: GPU training is 10-15x faster than CPU!")
    print("📊 Progress will be logged every 50 steps")
    print("💾 Checkpoints saved every 500 steps to:", output_dir)
    print("="*70 + "\n")
    
    try:
        trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        
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
