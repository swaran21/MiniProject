# Recipe ML Training - Quick Start Guide

## 📦 What's in This Package

This folder contains everything you need to train a recipe generation AI model using GPT-2:

- **prepare_recipe_data.py** - Prepares training data from recipe JSON files
- **train_recipe_model_cpu.py** - Trains model on CPU (slow, 8-10 hours)
- **train_recipe_model_gpu.py** - Trains model on GPU (fast, 2-3 hours)
- **test_recipe_generation.py** - Tests trained model with sample ingredients
- **checkpoint-3000.zip** - Pre-trained checkpoint (45% complete, ~330MB)
- **recipe_training.zip** - Training dataset (~17MB)

---

## 🚀 Quick Start (RTX 3050 Laptop)

### 1. Extract Files
```bash
# Create project directory
mkdir -p ~/MiniProject/pythonML
cd ~/MiniProject/pythonML

# Copy Python scripts
cp ~/Desktop/ML_Transfer/*.py .

# Extract checkpoint
mkdir -p app/models/recipe_gpt2
unzip ~/Desktop/ML_Transfer/checkpoint-3000.zip -d app/models/recipe_gpt2/

# Extract training data
mkdir -p data
unzip ~/Desktop/ML_Transfer/recipe_training.zip -d data/
```

### 2. Install Dependencies
```bash
# Install PyTorch with CUDA support (for GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install transformers datasets accelerate

# Verify GPU is detected
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"Not found\"}')"
```

### 3. Resume Training
```bash
# Start GPU training (resumes from checkpoint-3000)
python train_recipe_model_gpu.py

# When asked "Resume from this checkpoint? (y/n)", type: y
```

**Training Time:** ~1-1.5 hours on RTX 3050 to complete remaining 55%

---

## ⏱️ Training Progress

| Stage | Steps | Device | Time | Status |
|-------|-------|--------|------|--------|
| Initial | 0 → 3000 (45%) | CPU | 12 hours | ✅ Done |
| **Continue** | **3000 → 6597 (55%)** | **RTX 3050** | **~1 hour** | ⏳ Next |

---

## 🧪 After Training Completes

### Test the Model
```bash
python test_recipe_generation.py
```

### Try Some Ingredients
```
Enter ingredients: tomato, onions, chicken
```

The model will generate a complete recipe with:
- Recipe title
- Ingredient quantities (e.g., "500g chicken, 2 onions...")
- Step-by-step instructions

---

## 🛠️ Troubleshooting

### GPU Not Detected
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"
```
If False, reinstall PyTorch with CUDA support

### Out of Memory Error
Edit `train_recipe_model_gpu.py` and reduce batch size:
```python
per_device_train_batch_size=4,  # Change from 8 to 4
```

### Checkpoint Not Found
Verify extraction:
```bash
ls app/models/recipe_gpt2/checkpoint-3000/
# Should show: config.json, model.safetensors, optimizer.pt, etc.
```

---

## 📊 System Requirements

**Minimum:**
- GPU: NVIDIA RTX 3050 (4GB VRAM)
- RAM: 16GB
- Storage: 2GB free space
- CUDA: 11.8 or higher

**Recommended:**
- Same as above

---

## 📝 Training From Scratch (Optional)

If you want to train from step 0 instead of using the checkpoint:

```bash
# Prepare data (if recipe_training.txt doesn't exist)
python prepare_recipe_data.py

# Train on GPU from scratch
python train_recipe_model_gpu.py
# When asked to resume, type: n
```

**Time:** 2-3 hours for full training on RTX 3050

---

## 🎯 What You'll Get

After training completes, you'll have an AI model that can:
- Generate unique recipes from simple ingredient lists
- Create realistic ingredient quantities
- Produce step-by-step cooking instructions
- Work with any combination of ingredients

**Example:**
```
Input: "pasta, garlic, olive oil, tomatoes"
Output: Full recipe with title, measured ingredients, and cooking steps
```

---

## 💡 Tips

1. **Start training before you sleep** - it will be done when you wake up!
2. **Monitor GPU temperature** - ensure proper cooling during training
3. **Keep checkpoints** - training saves progress every 500 steps
4. **Test early** - run `test_recipe_generation.py` after training completes

---

## 📚 Additional Resources

- PyTorch Documentation: https://pytorch.org/docs/
- Hugging Face Transformers: https://huggingface.co/docs/transformers/
- DistilGPT2 Model Card: https://huggingface.co/distilgpt2

---

**Good luck with your training!** 🚀
