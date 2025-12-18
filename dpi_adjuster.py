from PIL import Image
import os
from pathlib import Path

def ensure_300_dpi(input_path, output_path):
    """
    Ensure image has at least 300 DPI, adjust if necessary
    """
    try:
        img = Image.open(input_path)
        
        # Get current DPI, default to 72x72 if missing
        dpi = img.info.get("dpi", (72, 72))
        x_dpi, y_dpi = dpi
        
        print(f"Current DPI: {x_dpi}x{y_dpi}")
        
        if x_dpi < 300 or y_dpi < 300:
            # Save with 300 DPI
            img.save(output_path, dpi=(300, 300), quality=95)
            print(f"✓ DPI increased to 300x300")
            return True, "modified"
        else:
            # Save with original DPI (already >= 300)
            img.save(output_path, dpi=dpi, quality=95)
            print(f"✓ DPI already >= 300, no change needed")
            return True, "unchanged"
            
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")
        return False, "error"

def process_all_images_dpi():
    """
    Process all images in images folder and adjust DPI to minimum 300
    """
    input_dir = "images"
    output_dir = "dpi_images"
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get all image files from images folder
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
    
    # Sort files for consistent processing
    image_files.sort()
    
    print("DPI ADJUSTMENT PROCESSOR")
    print("=" * 45)
    print(f"Found {len(image_files)} images to process.")
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print("Process:")
    print("- Check current DPI of each image")
    print("- Set DPI to 300x300 if less than 300")
    print("- Keep original DPI if already >= 300")
    print("- Save all images to dpi_images folder")
    print("-" * 45)
    
    successful = 0
    failed = 0
    modified_count = 0
    unchanged_count = 0
    
    for img_path in image_files:
        try:
            filename = os.path.basename(img_path)
            # Keep original filename and extension
            output_path = os.path.join(output_dir, filename)
            
            print(f"\nProcessing: {filename}")
            
            success, status = ensure_300_dpi(img_path, output_path)
            
            if success:
                successful += 1
                if status == "modified":
                    modified_count += 1
                elif status == "unchanged":
                    unchanged_count += 1
                print(f"✓ Saved: {filename}")
            else:
                failed += 1
                
        except Exception as e:
            print(f"✗ Error processing {img_path}: {str(e)}")
            failed += 1
    
    print("\n" + "-" * 45)
    print(f"DPI ADJUSTMENT COMPLETE!")
    print(f"✓ Successfully processed: {successful} images")
    print(f"📈 DPI modified (set to 300): {modified_count} images")
    print(f"📊 DPI unchanged (already >= 300): {unchanged_count} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"All processed images saved in '{output_dir}' directory.")
    print("Images now have minimum 300 DPI for high-quality printing!")

def check_image_dpi(image_path):
    """
    Check and display DPI information for a specific image
    """
    try:
        img = Image.open(image_path)
        dpi = img.info.get("dpi", (72, 72))
        x_dpi, y_dpi = dpi
        
        print(f"Image: {os.path.basename(image_path)}")
        print(f"Size: {img.size[0]}x{img.size[1]} pixels")
        print(f"DPI: {x_dpi}x{y_dpi}")
        print(f"Format: {img.format}")
        
        if x_dpi < 300 or y_dpi < 300:
            print("⚠️  DPI is less than 300 - needs adjustment")
        else:
            print("✅ DPI is 300 or higher - good for printing")
            
        return dpi
        
    except Exception as e:
        print(f"✗ Error reading {image_path}: {str(e)}")
        return None

def batch_check_dpi():
    """
    Check DPI of all images in the images folder
    """
    input_dir = "images"
    
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
    
    print("DPI CHECK REPORT")
    print("=" * 30)
    
    low_dpi_count = 0
    high_dpi_count = 0
    
    for img_path in sorted(image_files):
        print()
        dpi = check_image_dpi(img_path)
        if dpi:
            x_dpi, y_dpi = dpi
            if x_dpi < 300 or y_dpi < 300:
                low_dpi_count += 1
            else:
                high_dpi_count += 1
    
    print("\n" + "=" * 30)
    print("SUMMARY:")
    print(f"📉 Images with DPI < 300: {low_dpi_count}")
    print(f"📈 Images with DPI >= 300: {high_dpi_count}")
    print(f"📊 Total images: {len(image_files)}")

if __name__ == "__main__":
    # First, check current DPI status
    print("Checking current DPI status of all images...")
    batch_check_dpi()
    
    print("\n" + "="*50)
    
    # Then process all images
    process_all_images_dpi()
