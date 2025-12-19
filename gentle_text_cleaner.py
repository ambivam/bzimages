import cv2
import numpy as np
import os
from pathlib import Path

def gentle_text_enhancement(image):
    """
    Gently enhance text by darkening grey areas without destroying readability
    """
    # Work with original color image to preserve quality
    if len(image.shape) == 3:
        # Convert to LAB color space for better luminance control
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
    else:
        l = image.copy()
        a = np.zeros_like(l)
        b = np.zeros_like(l)
    
    # Enhance contrast in the L channel to darken grey text
    # Apply CLAHE for local contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    l_enhanced = clahe.apply(l)
    
    # Apply gamma correction to darken mid-tones (grey text)
    gamma = 0.7  # Darken grey areas
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    l_gamma = cv2.LUT(l_enhanced, table)
    
    # Merge back to BGR
    if len(image.shape) == 3:
        enhanced_lab = cv2.merge([l_gamma, a, b])
        result = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    else:
        result = l_gamma
    
    return result

def super_resolution_upscale(image, scale_factor=4):
    """
    High-quality super resolution upscaling using OpenCV
    """
    height, width = image.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # Use INTER_LANCZOS4 for highest quality upscaling
    upscaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    return upscaled

def sharpen_text_edges(image):
    """
    Lightly sharpen text edges to reduce outline blur
    """
    # Create a subtle sharpening kernel
    kernel = np.array([[-0.1, -0.2, -0.1],
                      [-0.2,  1.8, -0.2],
                      [-0.1, -0.2, -0.1]])
    
    # Apply sharpening
    sharpened = cv2.filter2D(image, -1, kernel)
    
    # Blend with original to avoid over-sharpening
    result = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)
    
    return result

def process_gentle_cleaning(input_path, output_path, scale_factor=4):
    """
    Gently clean text while preserving readability and add super resolution upscaling
    """
    try:
        # Handle UTF-8 encoding
        try:
            image = cv2.imread(input_path)
            if image is None:
                with open(input_path, 'rb') as f:
                    file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"✗ Encoding error reading {input_path}: {str(e)}")
            return False
            
        if image is None:
            print(f"✗ Could not read image: {input_path}")
            return False
        
        print(f"Processing: {os.path.basename(input_path)}")
        print(f"Original size: {image.shape[1]}x{image.shape[0]}")
        
        # Apply gentle text enhancement
        enhanced = gentle_text_enhancement(image)
        
        # Apply super resolution upscaling
        upscaled = super_resolution_upscale(enhanced, scale_factor)
        
        # Apply light sharpening to clean edges after upscaling
        cleaned = sharpen_text_edges(upscaled)
        
        print(f"Enhanced size: {cleaned.shape[1]}x{cleaned.shape[0]} ({scale_factor}x upscaled)")
        
        # Save with high quality
        success = cv2.imwrite(output_path, cleaned, 
                             [cv2.IMWRITE_PNG_COMPRESSION, 1])
        
        if success:
            print(f"✓ Super Resolution Enhanced: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
        else:
            print(f"✗ Failed to save: {output_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")
        return False

def clean_text_gently():
    """
    Process all images with gentle text cleaning that preserves readability
    """
    input_dir = "dpi_images"
    output_dir = "output_gentle"
    
    # Create directories
    Path(input_dir).mkdir(exist_ok=True)
    Path(output_dir).mkdir(exist_ok=True)
    
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
    
    print("GENTLE TEXT ENHANCEMENT + SUPER RESOLUTION")
    print("=" * 50)
    print(f"Found {len(image_files)} images to process.")
    print("Features:")
    print("- Darken grey text to black")
    print("- Preserve text readability")
    print("- 4x Super Resolution upscaling")
    print("- INTER_LANCZOS4 high-quality interpolation")
    print("- Light edge sharpening")
    print("- CLAHE contrast enhancement")
    print("- Gamma correction for mid-tones")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for img_path in image_files:
        filename = Path(img_path).stem
        output_path = os.path.join(output_dir, f"{filename}_gentle.png")
        
        if process_gentle_cleaning(img_path, output_path, scale_factor=4):
            successful += 1
        else:
            failed += 1
        print()
    
    print("-" * 50)
    print(f"GENTLE TEXT ENHANCEMENT + SUPER RESOLUTION COMPLETE!")
    print(f"✓ Successfully processed: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"Super resolution enhanced images saved in '{output_dir}' directory.")
    print("Text is now darker, more readable, and 4x higher resolution!")

if __name__ == "__main__":
    clean_text_gently()
