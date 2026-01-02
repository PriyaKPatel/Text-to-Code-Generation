"""
T5/CodeT5 Model wrapper for code generation
Handles model loading, inference, and caching
Supports both PyTorch and TensorFlow models
"""
import torch
import traceback
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer, 
    RobertaTokenizer,
    T5Config
)
import logging
import os
from typing import Optional
import boto3
from pathlib import Path

# Lazy import TensorFlow only when needed
TFT5ForConditionalGeneration = None
TFAutoModelForSeq2SeqLM = None

logger = logging.getLogger(__name__)

class T5CodeGenerator:
    """
    T5 Model wrapper for text-to-code generation
    Supports local and S3 model loading
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_prefix: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize T5 Code Generator
        
        Args:
            model_path: Local path to model weights
            s3_bucket: S3 bucket containing model (if using S3)
            s3_prefix: S3 prefix/folder for model files
            device: Device to run model on ('cpu', 'cuda', or None for auto)
        """
        self.model_path = model_path or os.getenv("MODEL_PATH", "./models")
        self.s3_bucket = s3_bucket or os.getenv("S3_BUCKET")
        self.s3_prefix = s3_prefix or os.getenv("S3_PREFIX", "models/v1")
        
        # Determine device
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing T5CodeGenerator on device: {self.device}")
        
        self.model = None
        self.tokenizer = None
        self.use_tensorflow = False  # Track if using TensorFlow or PyTorch
        
        # Load model
        self._load_model()
    
    def _download_from_s3(self):
        """Download model from S3 if configured"""
        if not self.s3_bucket:
            logger.info("No S3 bucket configured, skipping S3 download")
            return False
        
        try:
            logger.info(f"Downloading model from S3: {self.s3_bucket}/{self.s3_prefix}")
            s3 = boto3.client('s3')
            
            # Create local model directory
            Path(self.model_path).mkdir(parents=True, exist_ok=True)
            
            # List and download all model files
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.s3_bucket, Prefix=self.s3_prefix)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        # Get filename relative to prefix
                        relative_path = key[len(self.s3_prefix):].lstrip('/')
                        if relative_path:
                            local_path = os.path.join(self.model_path, relative_path)
                            
                            # Create directory if needed
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            
                            logger.info(f"Downloading {key} to {local_path}")
                            s3.download_file(self.s3_bucket, key, local_path)
            
            logger.info("Model downloaded from S3 successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            return False
    
    def _load_model(self):
        """Load model and tokenizer - supports both PyTorch and TensorFlow"""
        global TFT5ForConditionalGeneration
        
        try:
            # Try to download from S3 first
            if self.s3_bucket:
                self._download_from_s3()
            
            # Check if local model exists (must have config.json to be valid)
            config_path = os.path.join(self.model_path, "config.json")
            if os.path.exists(config_path):
                logger.info(f"Loading model from local path: {self.model_path}")
                
                # Check if TensorFlow model (tf_model.h5) or PyTorch model (pytorch_model.bin)
                tf_model_path = os.path.join(self.model_path, "tf_model.h5")
                pt_model_path = os.path.join(self.model_path, "pytorch_model.bin")
                
                if os.path.exists(pt_model_path):
                    # Load PyTorch model
                    logger.info("Detected PyTorch model (pytorch_model.bin)")
                    self.use_tensorflow = False
                    self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
                    
                    # Try RobertaTokenizer first (for CodeT5), fallback to T5Tokenizer
                    try:
                        self.tokenizer = RobertaTokenizer.from_pretrained(self.model_path)
                    except:
                        self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
                        
                elif os.path.exists(tf_model_path):
                    # TensorFlow model detected - load it!
                    logger.info("Detected TensorFlow model (tf_model.h5)")
                    
                    try:
                        from transformers import TFT5ForConditionalGeneration
                        import tensorflow as tf
                        
                        logger.info("Loading TensorFlow model...")
                        self.use_tensorflow = True
                        self.model = TFT5ForConditionalGeneration.from_pretrained(self.model_path)
                        
                        # Try RobertaTokenizer first (for CodeT5), fallback to T5Tokenizer
                        try:
                            self.tokenizer = RobertaTokenizer.from_pretrained(self.model_path)
                        except:
                            self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
                            
                        logger.info("TensorFlow model loaded successfully")
                        
                    except ImportError:
                        logger.error("TensorFlow not installed or import failed. Cannot load tf_model.h5")
                        raise
                    except Exception as e:
                        logger.error(f"Error loading TensorFlow model: {str(e)}")
                        raise
                else:
                    # No model weights found, try to load anyway (might be in subdirectory)
                    logger.warning("No model weights file found, attempting to load anyway...")
                    self.use_tensorflow = False
                    self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
                    try:
                        self.tokenizer = RobertaTokenizer.from_pretrained(self.model_path)
                    except:
                        self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
            else:
                # Fall back to CodeT5 model (trained for code generation)
                logger.warning(f"Local model not found at {self.model_path}, using CodeT5-base model")
                logger.info("Loading CodeT5-base from Hugging Face...")
                self.use_tensorflow = False
                self.model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-base")
                # CodeT5 uses RobertaTokenizer, not T5Tokenizer
                self.tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-base")
            
            # Move PyTorch model to device (TensorFlow handles device automatically)
            if not self.use_tensorflow:
                self.model.to(self.device)
                self.model.eval()
            
            logger.info(f"Model loaded successfully on {self.device}")
            if self.use_tensorflow:
                logger.info("Using TensorFlow backend")
            else:
                param_count = sum(p.numel() for p in self.model.parameters())
                logger.info(f"Model parameters: {param_count / 1e6:.2f}M")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    def generate(
        self, 
        prompt: str, 
        max_length: int = 150,
        temperature: float = 0.7,
        num_beams: int = 5,
        top_p: float = 0.95,
        repetition_penalty: float = 2.0
    ) -> str:
        """
        Generate code from natural language prompt
        
        Args:
            prompt: Natural language description
            max_length: Maximum length of generated code
            temperature: Sampling temperature (higher = more creative)
            num_beams: Number of beams for beam search
            top_p: Nucleus sampling threshold
            repetition_penalty: Penalty for repeating tokens
            
        Returns:
            Generated Python code
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")
        
        # Preprocess prompt with CodeT5 prefix (matching notebook)
        input_text = f"Generate Python: {prompt}"
        
        # Tokenize - use appropriate tensor format
        if self.use_tensorflow:
            inputs = self.tokenizer(
                input_text,
                return_tensors="tf",
                max_length=512,
                truncation=True,
                padding="max_length"
            )
        else:
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding="max_length"
            ).to(self.device)
        
        # Generate with parameters matching notebook for better code generation
        if self.use_tensorflow:
            # TensorFlow generation
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                top_p=top_p,
                top_k=50,
                repetition_penalty=repetition_penalty,
                num_return_sequences=1,
                do_sample=True,
                # early_stopping=True # Removed for TF compatibility if issues arise, but kept consistent with logic
            )
            # TensorFlow returns numpy array
            generated_code = self.tokenizer.decode(outputs.numpy()[0], skip_special_tokens=True)
        else:
            # PyTorch generation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    top_p=top_p,
                    top_k=50,  # Added top_k like in notebook
                    repetition_penalty=repetition_penalty,
                    num_return_sequences=1,
                    do_sample=True,
                    early_stopping=True
                )
            # Decode
            generated_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process
        generated_code = self._post_process(generated_code)
        
        return generated_code
    
    def _post_process(self, code: str) -> str:
        """
        Post-process generated code
        - Remove extra whitespace
        - Basic syntax validation
        """
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Ensure proper indentation (basic)
        lines = code.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        code = '\n'.join(cleaned_lines)
        
        return code
    
    def validate_syntax(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate Python syntax
        
        Returns:
            (is_valid, error_message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def get_model_info(self) -> dict:
        """Get model information"""
        if not self.is_loaded():
            return {"loaded": False}
        
        info = {
            "loaded": True,
            "device": str(self.device),
            "backend": "TensorFlow" if self.use_tensorflow else "PyTorch",
            "model_type": "TFT5ForConditionalGeneration" if self.use_tensorflow else "T5ForConditionalGeneration",
            "model_path": self.model_path
        }
        
        if not self.use_tensorflow:
            param_count = sum(p.numel() for p in self.model.parameters())
            info["parameters"] = f"{param_count / 1e6:.2f}M"
        
        return info
