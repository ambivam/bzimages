from PIL import Image
import os
from pathlib import Path

def convert_images_to_pdf():
    """
    Convert images from output_gentle folder to PDF format using Pillow
    """
    input_dir = "output_gentle"
    output_dir = "pdfs_pillow_output"
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get all image files from output_gentle folder
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
    
    # Sort files for consistent ordering
    image_files.sort()
    
    print("PILLOW PDF CONVERTER")
    print("=" * 40)
    print(f"Found {len(image_files)} images to convert.")
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print("Features:")
    print("- High resolution PDF (300 DPI)")
    print("- RGB color conversion")
    print("- Individual PDF per image")
    print("- Batch PDF creation option")
    print("-" * 40)
    
    successful = 0
    failed = 0
    
    # Convert each image to individual PDF
    for img_path in image_files:
        try:
            filename = Path(img_path).stem
            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
            
            print(f"Converting: {os.path.basename(img_path)}")
            
            # Open and convert image to RGB
            img = Image.open(img_path).convert("RGB")
            
            # Save as PDF with high resolution
            img.save(pdf_path, "PDF", resolution=300, quality=95)
            
            print(f"✓ PDF Created: {os.path.basename(img_path)} -> {os.path.basename(pdf_path)}")
            successful += 1
            
        except Exception as e:
            print(f"✗ Error converting {img_path}: {str(e)}")
            failed += 1
        
        print()
    
    # Create a combined PDF with all images
    try:
        print("Creating combined PDF with all images...")
        combined_pdf_path = os.path.join(output_dir, "all_images_combined.pdf")
        
        img_list = []
        for img_path in image_files:
            try:
                img = Image.open(img_path).convert("RGB")
                img_list.append(img)
            except Exception as e:
                print(f"✗ Error loading {img_path} for combined PDF: {str(e)}")
        
        if img_list:
            # Save combined PDF
            img_list[0].save(
                combined_pdf_path,
                save_all=True,
                append_images=img_list[1:],
                resolution=300,
                quality=95
            )
            print(f"✓ Combined PDF Created: all_images_combined.pdf ({len(img_list)} pages)")
        else:
            print("✗ No images available for combined PDF")
            
    except Exception as e:
        print(f"✗ Error creating combined PDF: {str(e)}")
    
    print("-" * 40)
    print(f"PDF CONVERSION COMPLETE!")
    print(f"✓ Successfully converted: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"PDFs saved in '{output_dir}' directory.")
    print("Individual PDFs + Combined PDF created with 300 DPI resolution!")

def convert_specific_images_to_pdf(image_names, output_name="custom_document.pdf"):
    """
    Convert specific images to a single PDF
    """
    input_dir = "output_gentle"
    output_dir = "pdfs_pillow_output"
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"Creating custom PDF: {output_name}")
    print(f"Images to include: {image_names}")
    
    try:
        img_list = []
        for img_name in image_names:
            img_path = os.path.join(input_dir, img_name)
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGB")
                img_list.append(img)
                print(f"✓ Added: {img_name}")
            else:
                print(f"✗ Not found: {img_name}")
        
        if img_list:
            pdf_path = os.path.join(output_dir, output_name)
            img_list[0].save(
                pdf_path,
                save_all=True,
                append_images=img_list[1:],
                resolution=300,
                quality=95
            )
            print(f"✓ Custom PDF Created: {output_name} ({len(img_list)} pages)")
            return True
        else:
            print("✗ No valid images found for custom PDF")
            return False
            
    except Exception as e:
        print(f"✗ Error creating custom PDF: {str(e)}")
        return False

if __name__ == "__main__":
    convert_images_to_pdf()
    
    # Example of creating a custom PDF with specific images
    # Uncomment and modify as needed:
    # convert_specific_images_to_pdf([
    #     "Imagem10_gentle.png",
    #     "Imagem11_gentle.png", 
    #     "Imagem12_gentle.png"
    # ], "sample_document.pdf")
