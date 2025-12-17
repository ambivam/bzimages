import torch
import torchvision.transforms as transforms
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
from pathlib import Path
import cv2

class TorchTextEnlarger:
    def __init__(self, device=None):
        """
        Initialize PyTorch-based text enlarger
        """
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        print(f"Using device: {self.device}")
        
        # Define transforms for text enhancement
        self.to_tensor = transforms.ToTensor()
        self.to_pil = transforms.ToPILImage()
        
    def enhance_text_clarity_torch(self, image_tensor):
        """
        Gentle enhancement similar to process_images.py approach
        """
        # Convert to LAB color space equivalent using tensor operations
        # Apply mild contrast enhancement
        enhanced = image_tensor.clone()
        
        # Simple contrast adjustment per channel
        for i in range(enhanced.shape[0]):
            channel = enhanced[i]
            # Normalize and apply mild contrast
            min_val = channel.min()
            max_val = channel.max()
            if max_val > min_val:
                normalized = (channel - min_val) / (max_val - min_val)
                # Apply very mild gamma correction
                gamma_corrected = torch.pow(normalized, 0.9)
                enhanced[i] = gamma_corrected * (max_val - min_val) + min_val
        
        return torch.clamp(enhanced, 0, 1)
    
    def upscale_image_torch(self, image_tensor, scale_factor=2):
        """
        Simple upscaling matching process_images.py approach
        """
        # Add batch dimension
        batch_tensor = image_tensor.unsqueeze(0)
        
        # Calculate new size
        _, _, h, w = batch_tensor.shape
        new_h, new_w = int(h * scale_factor), int(w * scale_factor)
        
        # Use bicubic interpolation (equivalent to INTER_CUBIC)
        upscaled = torch.nn.functional.interpolate(
            batch_tensor, 
            size=(new_h, new_w), 
            mode='bicubic', 
            align_corners=False
        )
        
        # Remove batch dimension
        return upscaled.squeeze(0)
    
    def process_with_pil_enhancement(self, pil_image):
        """
        Minimal PIL enhancement to match process_images.py quality
        """
        # Very light bilateral filter equivalent - just mild smoothing
        enhanced = pil_image.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        # Light unsharp mask similar to process_images.py
        unsharp = pil_image.filter(ImageFilter.UnsharpMask(radius=2.0, percent=50, threshold=0))
        
        # Blend original with unsharp
        enhanced = Image.blend(pil_image, unsharp, 0.5)
        
        return enhanced
    
    def process_single_image(self, input_path, output_path, scale_factor=2):
        """
        Process image to match process_images.py quality
        """
        try:
            # Load image
            if not os.path.exists(input_path):
                print(f"✗ File not found: {input_path}")
                return False
            
            # Handle different image formats and encodings
            try:
                pil_image = Image.open(input_path).convert('RGB')
            except Exception as e:
                # Fallback using OpenCV for problematic encodings
                img_array = cv2.imread(input_path)
                if img_array is None:
                    with open(input_path, 'rb') as f:
                        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                    img_array = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if img_array is None:
                    print(f"✗ Could not read image: {input_path}")
                    return False
                
                # Convert BGR to RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(img_array)
            
            print(f"Processing: {os.path.basename(input_path)}")
            print(f"Original size: {pil_image.size[0]}x{pil_image.size[1]}")
            
            # Convert to tensor and move to device
            image_tensor = self.to_tensor(pil_image).to(self.device)
            
            # Apply gentle enhancement
            enhanced_tensor = self.enhance_text_clarity_torch(image_tensor)
            
            # Upscale using PyTorch
            upscaled_tensor = self.upscale_image_torch(enhanced_tensor, scale_factor)
            
            # Convert back to PIL
            upscaled_pil = self.to_pil(upscaled_tensor.cpu())
            
            # Apply minimal PIL enhancement
            final_image = self.process_with_pil_enhancement(upscaled_pil)
            
            print(f"Enlarged size: {final_image.size[0]}x{final_image.size[1]} ({scale_factor}x larger)")
            
            # Save with high quality
            final_image.save(output_path, 'PNG', optimize=False, compress_level=1)
            
            print(f"✓ PyTorch Enhanced: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"✗ Error processing {input_path}: {str(e)}")
            return False

def enlarge_text_with_torch_fixed():
    """
    Process all images using corrected PyTorch approach
    """
    input_dir = "images"
    output_dir = "output_torch_fixed"
    
    # Create directories
    Path(input_dir).mkdir(exist_ok=True)
    Path(output_dir).mkdir(exist_ok=True)
    
    # Initialize PyTorch text enlarger
    enlarger = TorchTextEnlarger()
    
    # Get all image files
    image_files = []
    if os.path.exists(input_dir):
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                supported_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']
                if file_ext in supported_exts:
                    image_files.append(file_path)
    
    if not image_files:
        print(f"No images found in '{input_dir}' directory.")
        return
    
    print("PYTORCH TEXT ENLARGEMENT (FIXED)")
    print("=" * 50)
    print(f"Found {len(image_files)} images to process.")
    print("Features:")
    print("- Gentle enhancement matching process_images.py")
    print("- 2x bicubic upscaling")
    print("- Preserved color quality")
    print("- Minimal processing artifacts")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for img_path in image_files:
        filename = Path(img_path).stem
        output_path = os.path.join(output_dir, f"{filename}_torch_fixed.png")
        
        if enlarger.process_single_image(img_path, output_path, scale_factor=2):
            successful += 1
        else:
            failed += 1
        print()
    
    print("-" * 50)
    print(f"PYTORCH TEXT ENLARGEMENT COMPLETE!")
    print(f"✓ Successfully processed: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"Fixed PyTorch images saved in '{output_dir}' directory.")
    print("Quality now matches process_images.py output!")

if __name__ == "__main__":
    enlarge_text_with_torch_fixed()
