import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_training():
    model_script = os.path.join(BASE_DIR, 'ml_models', 'train_model.py')
    
    print("\nStarting EnergyAI ML Pipeline via Django Command...\n")
    try:
        subprocess.run([sys.executable, model_script], check=True)
        
        print("\n--- Model Artifact Sizes ---")
        artifacts = ['tfidf_vectorizer.pkl', 'intent_classifier.pkl', 'label_encoder.pkl']
        for file in artifacts:
            path = os.path.join(BASE_DIR, 'ml_models', file)
            if os.path.exists(path):
                size_kb = os.path.getsize(path) / 1024
                if size_kb > 1024:
                    print(f"  {file} — {size_kb/1024:.1f} MB")
                else:
                    print(f"  {file} — {size_kb:.1f} KB")
                    
        print("\nEnergyAI chatbot model trained successfully.")
        print("Run the server and navigate to /chat/ to test.\n")

    except subprocess.CalledProcessError as e:
        print(f"Error during training: {e}")

if __name__ == "__main__":
    run_training()
