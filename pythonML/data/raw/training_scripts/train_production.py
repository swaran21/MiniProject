"""
PRODUCTION TRAINING SCRIPT - GPT2-Medium
Optimized for RTX 3050 (4GB VRAM)
Trains on curated 50k recipes for high quality output
"""
import os
import torch
from pathlib import Path
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)

def main():
    print("="*80)
    print("RECIPE MODEL TRAINING - PRODUCTION VERSION")
    print("Using GPT2-Medium for Better Quality")
    print("="*80)
    
    # GPU Check
    print(f"\n🔧 Hardware:")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"   ✅ GPU: {gpu_name}")
        print(f"   Memory: {gpu_memory:.1f} GB")
    else:
        print("   ❌ No CUDA GPU! Install PyTorch with CUDA:")
        print("   pip install torch --index-url https://download.pytorch.org/whl/cu118")
        return
    
    # Check dataset
    data_file = 'data/recipe_training_CURATED.txt'
    if not Path(data_file).exists():
        print(f"\n❌ Dataset not found: {data_file}")
        return
    
    file_size = Path(data_file).stat().st_size / 1024**2
    print(f"\n📊 Dataset:")
    print(f"   File: {data_file}")
    print(f"   Size: {file_size:.1f} MB")
    print(f"   Quality: CURATED (50k best recipes)")
    
    # Load tokenizer and model
    print(f"\n🔧 Loading GPT2-Medium...")
    print("   (Bigger than DistilGPT2 = Better Quality)")
    
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
    tokenizer.pad_token = tokenizer.eos_token
    
    model = GPT2LMHeadModel.from_pretrained('gpt2-medium')
    print(f"   Parameters: {model.num_parameters():,}")
    print(f"   (vs DistilGPT2: 82M - this is better!)")
    
    # Prepare dataset
    print(f"\n📚 Loading training data...")
    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=data_file,
        block_size=128
    )
    print(f"   Training samples: {len(train_dataset):,}")
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Output directory
    output_dir = 'app/models/recipe_gpt2'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # OPTIMIZED Training Configuration
    print(f"\n⚙️  Training Configuration:")
    print("   Model: GPT2-Medium")
    print("   Dataset: 50k curated recipes")
    print("   Epochs: 3 (more thorough learning)")
    print("   Batch Size: 2 (fits in 4GB)")
    print("   Gradient Accumulation: 8 (effective batch=16)")
    print("   Learning Rate: 3e-5 (conservative)")
    print("   FP16: Yes (memory efficient)")
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,  # More epochs for better learning
        per_device_train_batch_size=2,  # Small for 4GB VRAM
        gradient_accumulation_steps=8,  # Effective batch = 2*8 = 16
        save_steps=2000,
        save_total_limit=2,
        logging_steps=100,
        logging_dir=f'{output_dir}/logs',
        fp16=True,
        learning_rate=3e-5,  # Lower = more stable
        warmup_steps=500,
        weight_decay=0.01,
        dataloader_num_workers=2,
        logging_first_step=True,
        prediction_loss_only=True,
        load_best_model_at_end=False,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    
    # Start training
    print(f"\n{'='*80}")
    print("🚀 STARTING TRAINING")
    print("="*80)
    print(f"⏰ Estimated time: 3-4 hours on RTX 3050")
    print(f"💾 Checkpoints will be saved every 2000 steps")
    print(f"📊 Progress logged every 100 steps")
    print(f"\n💡 You can leave this running - it will save automatically!")
    print("="*80 + "\n")
    
    try:
        # Train
        trainer.train()
        
        print(f"\n{'='*80}")
        print("✅ TRAINING COMPLETE!")
        print("="*80)
        
        # Save final model
        print(f"\n💾 Saving final model...")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        print(f"\n✅ SUCCESS!")
        print(f"\nModel saved to: {output_dir}")
        print(f"\n📝 Next steps:")
        print(f"   1. Transfer app/models/recipe_gpt2/ back to main laptop")
        print(f"   2. Restart Python backend")
        print(f"   3. Test with Kimchi/Tofu/Rice for Korean cuisine")
        print(f"   4. Enjoy much better recipes!")
        print("="*80)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Training interrupted")
        print(f"Latest checkpoint saved in {output_dir}")
    except Exception as e:
        print(f"\n\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
