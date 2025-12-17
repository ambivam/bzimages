import img2pdf
import os
from pathlib import Path

def convert_images_with_img2pdf():
    """
    Convert images from output_gentle folder to PDF format using img2pdf
    """
    input_dir = "output_gentle"
    output_dir = "pdfs_image2pdf_output"
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get all image files from output_gentle folder
    image_files = []
    if os.path.exists(input_dir):
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                supported_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
                if file_ext in supported_exts:
                    image_files.append(file_path)
    
    if not image_files:
        print(f"No images found in '{input_dir}' directory.")
        return
    
    # Sort files for consistent ordering
    image_files.sort()
    
    print("IMG2PDF CONVERTER")
    print("=" * 35)
    print(f"Found {len(image_files)} images to convert.")
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print("Features:")
    print("- Lossless PDF conversion")
    print("- Preserves original image quality")
    print("- Individual PDF per image")
    print("- Combined PDF with all images")
    print("- Fast conversion using img2pdf")
    print("-" * 35)
    
    successful = 0
    failed = 0
    
    # Convert each image to individual PDF
    for img_path in image_files:
        try:
            filename = Path(img_path).stem
            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
            
            print(f"Converting: {os.path.basename(img_path)}")
            
            # Convert single image to PDF using img2pdf
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert([img_path]))
            
            print(f"✓ PDF Created: {os.path.basename(img_path)} -> {os.path.basename(pdf_path)}")
            successful += 1
            
        except Exception as e:
            print(f"✗ Error converting {img_path}: {str(e)}")
            failed += 1
        
        print()
    
    # Create a combined PDF with all images
    try:
        print("Creating combined PDF with all images...")
        combined_pdf_path = os.path.join(output_dir, "all_images_combined_img2pdf.pdf")
        
        # Convert all images to single PDF using img2pdf
        with open(combined_pdf_path, "wb") as f:
            f.write(img2pdf.convert(image_files))
        
        print(f"✓ Combined PDF Created: all_images_combined_img2pdf.pdf ({len(image_files)} pages)")
        
    except Exception as e:
        print(f"✗ Error creating combined PDF: {str(e)}")
    
    print("-" * 35)
    print(f"IMG2PDF CONVERSION COMPLETE!")
    print(f"✓ Successfully converted: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"PDFs saved in '{output_dir}' directory.")
    print("Lossless PDF conversion with original image quality preserved!")

def convert_specific_images_with_img2pdf(image_names, output_name="custom_document_img2pdf.pdf"):
    """
    Convert specific images to a single PDF using img2pdf
    """
    input_dir = "output_gentle"
    output_dir = "pdfs_image2pdf_output"
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"Creating custom PDF with img2pdf: {output_name}")
    print(f"Images to include: {image_names}")
    
    try:
        valid_images = []
        for img_name in image_names:
            img_path = os.path.join(input_dir, img_name)
            if os.path.exists(img_path):
                valid_images.append(img_path)
                print(f"✓ Added: {img_name}")
            else:
                print(f"✗ Not found: {img_name}")
        
        if valid_images:
            pdf_path = os.path.join(output_dir, output_name)
            
            # Convert selected images to PDF using img2pdf
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert(valid_images))
            
            print(f"✓ Custom PDF Created: {output_name} ({len(valid_images)} pages)")
            return True
        else:
            print("✗ No valid images found for custom PDF")
            return False
            
    except Exception as e:
        print(f"✗ Error creating custom PDF: {str(e)}")
        return False

def batch_convert_by_groups(group_size=5):
    """
    Convert images in groups to separate PDFs
    """
    input_dir = "output_gentle"
    output_dir = "pdfs_image2pdf_output"
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get all image files
    image_files = []
    if os.path.exists(input_dir):
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                supported_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
                if file_ext in supported_exts:
                    image_files.append(file_path)
    
    if not image_files:
        print(f"No images found in '{input_dir}' directory.")
        return
    
    # Sort files
    image_files.sort()
    
    print(f"Creating group PDFs with {group_size} images per PDF...")
    
    # Split into groups and create PDFs
    for i in range(0, len(image_files), group_size):
        group = image_files[i:i+group_size]
        group_num = (i // group_size) + 1
        pdf_path = os.path.join(output_dir, f"group_{group_num:02d}_img2pdf.pdf")
        
        try:
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert(group))
            
            print(f"✓ Group PDF {group_num}: {len(group)} images -> group_{group_num:02d}_img2pdf.pdf")
            
        except Exception as e:
            print(f"✗ Error creating group PDF {group_num}: {str(e)}")

if __name__ == "__main__":
    convert_images_with_img2pdf()
    
    # Example of creating group PDFs (uncomment to use)
    # print("\n" + "="*35)
    # batch_convert_by_groups(group_size=5)
    
    # Example of creating a custom PDF with specific images (uncomment to use)
    # print("\n" + "="*35)
    # convert_specific_images_with_img2pdf([
    #     "Imagem10_gentle.png",
    #     "Imagem11_gentle.png", 
    #     "Imagem12_gentle.png"
    # ], "sample_document_img2pdf.pdf")
