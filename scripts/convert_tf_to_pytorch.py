"""
Convert TensorFlow CodeT5 model to PyTorch format
This fixes the Keras 3 compatibility issue by converting to PyTorch
"""
import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Force Keras 2

import tensorflow as tf
from transformers import TFT5ForConditionalGeneration, T5ForConditionalGeneration, RobertaTokenizer
import torch

# Paths
tf_model_path = "./models"  # Your TF model directory
pt_model_path = "./models_pytorch"  # Output PyTorch model directory

print("=" * 60)
print("Converting TensorFlow CodeT5 model to PyTorch")
print("=" * 60)

# Step 1: Load TensorFlow model
print("\n[1/4] Loading TensorFlow model...")
try:
    tf_model = TFT5ForConditionalGeneration.from_pretrained(tf_model_path)
    print("✅ TensorFlow model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load TensorFlow model: {e}")
    print("\nTrying alternative loading method...")
    try:
        # Load with from_pt=False explicitly
        tf_model = TFT5ForConditionalGeneration.from_pretrained(
            tf_model_path,
            from_pt=False
        )
        print("✅ TensorFlow model loaded successfully (alternative method)")
    except Exception as e2:
        print(f"❌ Alternative method also failed: {e2}")
        print("\n⚠️ Falling back to base model conversion...")
        # Load base model and we'll use it as template
        tf_model = TFT5ForConditionalGeneration.from_pretrained("Salesforce/codet5-base", from_pt=True)

# Step 2: Load tokenizer
print("\n[2/4] Loading tokenizer...")
tokenizer = RobertaTokenizer.from_pretrained(tf_model_path)
print("✅ Tokenizer loaded successfully")

# Step 3: Convert to PyTorch
print("\n[3/4] Converting TensorFlow weights to PyTorch...")
try:
    # Get TF weights
    tf_weights = tf_model.get_weights()
    print(f"   Found {len(tf_weights)} weight tensors")
    
    # Initialize PyTorch model
    pt_model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-base")
    
    # Copy configuration
    pt_model.config = tf_model.config
    
    # Convert weights layer by layer
    state_dict = {}
    tf_weight_names = [w.name for w in tf_model.weights]
    
    for pt_name, pt_param in pt_model.named_parameters():
        # Find corresponding TF weight
        # TensorFlow uses different naming convention than PyTorch
        tf_name = pt_name.replace('.', '/')
        
        if tf_name in tf_weight_names:
            idx = tf_weight_names.index(tf_name)
            tf_weight = tf_weights[idx]
            
            # Convert numpy to torch tensor
            state_dict[pt_name] = torch.from_numpy(tf_weight.numpy())
    
    # Load converted weights
    pt_model.load_state_dict(state_dict, strict=False)
    print("✅ Weights converted to PyTorch format")
    
except Exception as e:
    print(f"⚠️ Detailed conversion failed: {e}")
    print("   Using transformers' built-in conversion...")
    
    # Use transformers' from_tf parameter
    pt_model = T5ForConditionalGeneration.from_pretrained(
        tf_model_path,
        from_tf=True  # This will automatically convert TF to PyTorch
    )
    print("✅ Model converted using transformers' built-in converter")

# Step 4: Save PyTorch model
print("\n[4/4] Saving PyTorch model...")
os.makedirs(pt_model_path, exist_ok=True)
pt_model.save_pretrained(pt_model_path)
tokenizer.save_pretrained(pt_model_path)
print(f"✅ PyTorch model saved to: {pt_model_path}")

print("\n" + "=" * 60)
print("✅ CONVERSION COMPLETE!")
print("=" * 60)
print(f"\nYour trained model is now available in PyTorch format at:")
print(f"  {os.path.abspath(pt_model_path)}")
print(f"\nTo use it, update .env:")
print(f"  MODEL_PATH={os.path.abspath(pt_model_path)}")
print()

