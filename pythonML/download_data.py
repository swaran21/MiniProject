import kagglehub
import os
import shutil

def download_kde_diet():
    print("Downloading Diet Recommendations Dataset (ziya07/diet-recommendations-dataset)...")
    try:
        # Download latest version
        path = kagglehub.dataset_download("ziya07/diet-recommendations-dataset")
        print(f"\nSUCCESS! Dataset downloaded to: {path}")
        
        # Define local target
        target_dir = os.path.join(os.getcwd(), "data", "diet_recommendations")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        # Copy files to local project folder for easier access
        print(f"Copying files to {target_dir}...")
        for file in os.listdir(path):
            src = os.path.join(path, file)
            dst = os.path.join(target_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f" - Copped {file}")
                
        print("\nDone! You can find the data in ./data/diet_recommendations/")
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("Make sure you have internet access and 'kagglehub' installed.")

if __name__ == "__main__":
    download_kde_diet()
    print("\n--- NOTE ON NUTRITION5K ---")
    print("Nutrition5k is VERY LARGE (180GB).")
    print("To download it, you need the Google Cloud SDK (gsutil).")
    print("See ML_RESOURCES.md for specific commands to download just the metadata first.")
