import cv2
import numpy as np
import os
from pathlib import Path

def clean_text_outlines(image):
    """
    Convert grey text to black and remove outlines around letters
    """
    # Convert to grayscale for processing
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Create a binary mask to identify text areas
    # Use adaptive thresholding to separate text from background
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    
    # Invert so text is white on black background
    binary_inv = cv2.bitwise_not(binary)
    
    # Apply morphological operations to clean up text edges
    # Use a small kernel to remove thin outlines
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    
    # Opening to remove small noise and thin outlines
    cleaned = cv2.morphologyEx(binary_inv, cv2.MORPH_OPEN, kernel)
    
    # Closing to fill small gaps in text
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close)
    
    # Create final image with pure black text on white background
    result = np.ones_like(gray) * 255  # White background
    result[cleaned > 0] = 0  # Black text
    
    # Convert back to BGR if original was color
    if len(image.shape) == 3:
        result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        return result_bgr
    else:
        return result

def clean_text_advanced(image):
    """
    Advanced text cleaning to remove grey color and outlines
    """
    # Convert to HSV for better color manipulation
    if len(image.shape) == 3:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        hsv = cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2HSV)
    
    # Create mask for text areas (darker regions)
    # Identify pixels that are darker than background
    _, text_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_mask = cv2.bitwise_not(text_mask)
    
    # Apply Gaussian blur to smooth edges
    blurred = cv2.GaussianBlur(text_mask, (3, 3), 0)
    
    # Apply stronger threshold to get clean black text
    _, clean_text = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    
    # Remove small noise with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    clean_text = cv2.morphologyEx(clean_text, cv2.MORPH_OPEN, kernel)
    
    # Fill small holes in text
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean_text = cv2.morphologyEx(clean_text, cv2.MORPH_CLOSE, kernel_close)
    
    # Create final result with pure black text
    result = np.ones_like(gray) * 255  # White background
    result[clean_text > 0] = 0  # Pure black text
    
    # Convert back to BGR
    if len(image.shape) == 3:
        result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        return result_bgr
    else:
        return result

def process_text_cleaning(input_path, output_path):
    """
    Process image to clean text outlines and convert grey to black
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
        
        # Apply advanced text cleaning
        cleaned = clean_text_advanced(image)
        
        # Save with high quality
        success = cv2.imwrite(output_path, cleaned, 
                             [cv2.IMWRITE_PNG_COMPRESSION, 0])
        
        if success:
            print(f"✓ Text Cleaned: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
        else:
            print(f"✗ Failed to save: {output_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")
        return False

def clean_all_text():
    """
    Process all images to clean text outlines and convert grey to black
    """
    input_dir = "images"
    output_dir = "output_cleaned"
    
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
    
    print("TEXT OUTLINE CLEANING")
    print("=" * 45)
    print(f"Found {len(image_files)} images to process.")
    print("Features:")
    print("- Convert grey text to pure black")
    print("- Remove outlines around letters")
    print("- Clean text edges with morphology")
    print("- Adaptive thresholding for clarity")
    print("- Pure black text on white background")
    print("-" * 45)
    
    successful = 0
    failed = 0
    
    for img_path in image_files:
        filename = Path(img_path).stem
        output_path = os.path.join(output_dir, f"{filename}_cleaned.png")
        
        if process_text_cleaning(img_path, output_path):
            successful += 1
        else:
            failed += 1
        print()
    
    print("-" * 45)
    print(f"TEXT CLEANING COMPLETE!")
    print(f"✓ Successfully processed: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"Cleaned images saved in '{output_dir}' directory.")
    print("Text is now pure black without outlines!")

if __name__ == "__main__":
    clean_all_text()
