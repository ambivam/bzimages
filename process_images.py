import cv2
import numpy as np
import os
import glob
from pathlib import Path

def enhance_image(image):
    """
    Apply various image enhancement techniques using OpenCV
    """
    # Convert to LAB color space for better processing
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Merge channels back
    enhanced_lab = cv2.merge([l, a, b])
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # Apply bilateral filter for noise reduction while preserving edges
    filtered = cv2.bilateralFilter(enhanced_bgr, 9, 75, 75)
    
    # Apply unsharp masking for sharpening
    gaussian = cv2.GaussianBlur(filtered, (0, 0), 2.0)
    sharpened = cv2.addWeighted(filtered, 1.5, gaussian, -0.5, 0)
    
    return sharpened

def upscale_image(image, scale_factor=2):
    """
    Upscale image using OpenCV's super resolution or interpolation
    """
    height, width = image.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # Use INTER_CUBIC for better quality upscaling
    upscaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    return upscaled

def process_single_image(input_path, output_path):
    """
    Process a single image with enhancement and upscaling
    """
    try:
        # Read image
        image = cv2.imread(input_path)
        if image is None:
            print(f"✗ Could not read image: {input_path}")
            return False
        
        # Apply image enhancement
        enhanced = enhance_image(image)
        
        # Upscale image
        processed = upscale_image(enhanced, scale_factor=2)
        
        # Save processed image
        success = cv2.imwrite(output_path, processed)
        
        if success:
            print(f"✓ Processed: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
        else:
            print(f"✗ Failed to save: {output_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")
        return False

def process_images():
    """
    Process all images from images folder and save to output folder
    """
    # Define directories
    input_dir = "images"
    output_dir = "output"
    
    # Create directories if they don't exist
    Path(input_dir).mkdir(exist_ok=True)
    Path(output_dir).mkdir(exist_ok=True)
    
    # Supported image formats
    supported_formats = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.webp']
    
    # Get all image files
    image_files = []
    for format in supported_formats:
        image_files.extend(glob.glob(os.path.join(input_dir, format)))
        image_files.extend(glob.glob(os.path.join(input_dir, format.upper())))
    
    if not image_files:
        print(f"No images found in '{input_dir}' directory.")
        print("Please add some images to the 'images' folder and try again.")
        print(f"Supported formats: {', '.join(supported_formats)}")
        return
    
    print(f"Found {len(image_files)} images to process.")
    print("Processing with: Enhancement + 2x Upscaling")
    print("-" * 50)
    
    # Process each image
    successful = 0
    failed = 0
    
    for img_path in image_files:
        # Get filename without extension
        filename = Path(img_path).stem
        
        # Create output path
        output_path = os.path.join(output_dir, f"{filename}_processed.png")
        
        # Process image
        if process_single_image(img_path, output_path):
            successful += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Processing complete!")
    print(f"✓ Successfully processed: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"Processed images saved in '{output_dir}' directory.")

if __name__ == "__main__":
    print("OpenCV Image Processor")
    print("=" * 50)
    process_images()
