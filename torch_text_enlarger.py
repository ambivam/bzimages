import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
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
        Enhance text clarity using PyTorch tensor operations - preserve color
        """
        # Work with original color channels to preserve quality
        original_tensor = image_tensor.clone()
        
        # Apply mild contrast enhancement per channel
        enhanced_channels = []
        for i in range(image_tensor.shape[0]):
            channel = image_tensor[i:i+1]
            
            # Mild contrast enhancement
            normalized = (channel - channel.min()) / (channel.max() - channel.min() + 1e-8)
            
            # Very light gamma correction
            gamma = 0.95
            gamma_corrected = torch.pow(normalized, gamma)
            
            enhanced_channels.append(gamma_corrected)
        
        enhanced_tensor = torch.cat(enhanced_channels, dim=0)
        
        # Apply very light sharpening to all channels
        sharpen_kernel = torch.tensor([[
            [0, -0.2, 0],
            [-0.2, 1.8, -0.2],
            [0, -0.2, 0]
        ]], dtype=torch.float32, device=self.device).unsqueeze(0).unsqueeze(0)
        
        # Apply sharpening to each channel separately
        sharpened_channels = []
        for i in range(enhanced_tensor.shape[0]):
            channel = enhanced_tensor[i:i+1].unsqueeze(0)
            padded = torch.nn.functional.pad(channel, (1, 1, 1, 1), mode='reflect')
            sharpened = torch.nn.functional.conv2d(padded, sharpen_kernel)
            sharpened = torch.clamp(sharpened.squeeze(0), 0, 1)
            sharpened_channels.append(sharpened)
        
        final_enhanced = torch.cat(sharpened_channels, dim=0)
        
        # Blend with original to preserve quality
        result = 0.7 * original_tensor + 0.3 * final_enhanced
        
        return torch.clamp(result, 0, 1)
    
    def upscale_image_torch(self, image_tensor, scale_factor=4):
        """
        Upscale image using PyTorch interpolation
        """
        # Add batch dimension
        batch_tensor = image_tensor.unsqueeze(0)
        
        # Calculate new size
        _, _, h, w = batch_tensor.shape
        new_h, new_w = int(h * scale_factor), int(w * scale_factor)
        
        # Use bicubic interpolation for high-quality upscaling
        upscaled = torch.nn.functional.interpolate(
            batch_tensor, 
            size=(new_h, new_w), 
            mode='bicubic', 
            align_corners=False,
            antialias=True
        )
        
        # Remove batch dimension
        return upscaled.squeeze(0)
    
    def process_with_pil_enhancement(self, pil_image):
        """
        Gentle PIL-based enhancements for text clarity
        """
        # Very mild contrast enhancement
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(1.05)
        
        # Light sharpness enhancement
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.1)
        
        # Gentle unsharp mask
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=2))
        
        return enhanced
    
    def process_single_image(self, input_path, output_path, scale_factor=4):
        """
        Process a single image with PyTorch-based text enlargement
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
            
            # Apply text clarity enhancement
            enhanced_tensor = self.enhance_text_clarity_torch(image_tensor)
            
            # Upscale using PyTorch
            upscaled_tensor = self.upscale_image_torch(enhanced_tensor, scale_factor)
            
            # Convert back to PIL for additional processing
            upscaled_pil = self.to_pil(upscaled_tensor.cpu())
            
            # Apply additional PIL-based enhancements
            final_image = self.process_with_pil_enhancement(upscaled_pil)
            
            print(f"Enlarged size: {final_image.size[0]}x{final_image.size[1]} ({scale_factor}x larger)")
            
            # Save with high quality
            final_image.save(output_path, 'PNG', optimize=False, compress_level=1)
            
            print(f"✓ PyTorch Enhanced: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"✗ Error processing {input_path}: {str(e)}")
            return False

def enlarge_text_with_torch():
    """
    Process all images using PyTorch for text enlargement
    """
    input_dir = "images"
    output_dir = "output_torch"
    
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
    
    print("PYTORCH TEXT ENLARGEMENT")
    print("=" * 50)
    print(f"Found {len(image_files)} images to process.")
    print("PyTorch Features:")
    print("- GPU acceleration (if available)")
    print("- Tensor-based image processing")
    print("- Bicubic interpolation upscaling")
    print("- Advanced contrast enhancement")
    print("- Convolution-based sharpening")
    print("- PIL UnsharpMask filtering")
    print("- 4x text enlargement")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for img_path in image_files:
        filename = Path(img_path).stem
        output_path = os.path.join(output_dir, f"{filename}_torch_enlarged.png")
        
        if enlarger.process_single_image(img_path, output_path, scale_factor=4):
            successful += 1
        else:
            failed += 1
        print()
    
    print("-" * 50)
    print(f"PYTORCH TEXT ENLARGEMENT COMPLETE!")
    print(f"✓ Successfully processed: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"PyTorch enhanced images saved in '{output_dir}' directory.")
    print("Text enlarged 4x with GPU-accelerated processing!")

if __name__ == "__main__":
    enlarge_text_with_torch()
