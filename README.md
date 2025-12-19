# OpenCV Image Processor

This project uses OpenCV with contrib modules to enhance and upscale images with various computer vision techniques, including specialized document text enhancement.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Activate virtual environment (if using):**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

## Usage

### General Image Processing
1. **Place your images** in the `images/` folder
   - Supported formats: JPG, JPEG, PNG, BMP, TIFF, WEBP

2. **Run the processing script:**
   ```bash
   python process_images.py
   ```

3. **Find processed images** in the `output/` folder
   - Images will be saved as `{original_name}_processed.png`

### Document Text Enhancement (Recommended for text clarity)
1. **Place your document images** in the `images/` folder
   - Best for scanned documents, financial reports, text-heavy images

2. **Run the document enhancement script:**
   ```bash
   python enhance_documents.py
   ```

3. **Find enhanced documents** in the `output/` folder
   - Images will be saved as `{original_name}_enhanced.png`

## Image Processing Features

### General Image Processing (`process_images.py`)
- **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Improves local contrast
- **Bilateral Filtering**: Reduces noise while preserving edges
- **Unsharp Masking**: Enhances image sharpness
- **2x Upscaling**: Uses cubic interpolation for better quality
- **LAB Color Space Processing**: Better color handling

### Document Text Enhancement (`enhance_documents.py`)
- **Text-Specific Sharpening**: Optimized for character clarity
- **Adaptive Thresholding**: Improves text definition
- **Morphological Operations**: Cleans up text artifacts
- **Noise Reduction**: Specialized for document processing
- **Super Resolution**: 2x upscaling optimized for text
- **Contrast Enhancement**: Better readability for documents

## Features

- **Batch processing**: Processes all images in the `images/` folder automatically
- **Error handling**: Continues processing even if individual images fail
- **Multiple formats**: Supports common image formats
- **Progress feedback**: Shows processing status for each image
- **High quality output**: PNG format with enhanced quality

## Directory Structure

```
brazil_images_realsgran/
├── images/              # Place input images here
├── output/              # Processed images appear here
├── process_images.py    # Main processing script
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Processing Pipeline

1. **Read Image**: Load image using OpenCV
2. **Color Space Conversion**: Convert BGR to LAB for better processing
3. **Contrast Enhancement**: Apply CLAHE to luminance channel
4. **Noise Reduction**: Apply bilateral filter
5. **Sharpening**: Apply unsharp masking
6. **Upscaling**: 2x upscale using cubic interpolation
7. **Save**: Output as PNG file

## Requirements

- Python 3.7+
- opencv-contrib-python
- numpy
- pillow


# Windows
set OPENAI_API_KEY=your-api-key-here

# macOS/Linux  
export OPENAI_API_KEY=your-api-key-here
