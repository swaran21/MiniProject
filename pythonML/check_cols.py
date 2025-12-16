import pandas as pd
df = pd.read_csv('data/diet_recommendations/diet_recommendations_dataset.csv')
print(f"Has Weight? {'Weight' in df.columns}")
print(f"Has Height? {'Height' in df.columns}")
print(f"Has BMI? {'BMI' in df.columns}")
print(f"Has weight? {'weight' in df.columns}")
print(f"Has height? {'height' in df.columns}")
print(f"Also has: {df.columns.tolist()[:5]}")
