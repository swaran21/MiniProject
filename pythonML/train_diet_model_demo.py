import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle
import os

# 1. Config
DATA_PATH = "data/diet_recommendations/diet_recommendations_dataset.csv"
MODEL_PATH = "app/models/diet_model.pkl"

def train_and_save():
    print("--- Starting Diet Recommender Training ---")
    
    # 2. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        print("Please run 'python download_data.py' first.")
        return

    print("Loading dataset...")
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Loaded {len(df)} rows.")
        print("Columns:", df.columns.tolist())
        
        # NOTE: This part depends on the EXACT columns of the Kaggle dataset.
        # Since I can't see the exact columns yet (Kaggle datasets vary), 
        # I will write a generic 'Content-Based' logic assuming some nutritional columns exist.
        # If the dataset is purely User-Item ratings, we would use SVD.
        
        # Let's inspect columns first in a real runtime, but here we'll assume 
        # it has nutritional info for a Content-Based approach (clustering similar foods).
        
        # We must only train on features that our 'UserProfile' can actually provide.
        # Verified columns: Age, Weight_kg, Height_cm, BMI
        
        target_features = ['Age', 'Weight_kg', 'Height_cm', 'BMI']
        
        # Check if they exist in dataset
        missing = [f for f in target_features if f not in df.columns]
        if missing:
            print(f"Warning: Dataset missing standard columns: {missing}")
            # Fallback to whatever numeric columns exist if our preferred ones aren't there
            final_features = df.select_dtypes(include=['number']).columns.tolist()
        else:
            final_features = target_features
            
        print(f"Training on STRICT features: {final_features}")
        
        # 4. Train Model (Nearest Neighbors)
        # We use a simple Nearest Neighbors to find 'similar patients'
        model = NearestNeighbors(n_neighbors=5, algorithm='auto')
        model.fit(df[final_features].fillna(0))
        
        print("Model trained successfully!")
        
        # Save feature list with model so we know what to input later
        model_data = {
            "model": model,
            "features": final_features
        }
        
        # 5. Save Model
        if not os.path.exists("app/models"):
            os.makedirs("app/models")
            
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_data, f)

            
        print(f"Model saved to {MODEL_PATH}")
        print("You can now load this in 'ml_service.py' to recommend similar foods!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    train_and_save()
