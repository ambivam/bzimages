import os
import json
from pathlib import Path
import shutil
from openai import OpenAI
import PyPDF2
from PIL import Image
import pytesseract
import fitz  # PyMuPDF for better PDF text extraction

class PDFGrouper:
    def __init__(self, api_key=None):
        """
        Initialize PDF Grouper with OpenAI API
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get API key from environment variable
            try:
                self.client = OpenAI()  # Will use OPENAI_API_KEY env var
            except Exception as e:
                print("⚠️  OpenAI API key not found. Please set OPENAI_API_KEY environment variable or pass api_key parameter.")
                print("Example: export OPENAI_API_KEY='your-api-key-here'")
                self.client = None
        
        self.input_dir = "pdfs_image2pdf_output"
        self.output_base_dir = "grouped_pdfs"
        
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF using multiple methods for better accuracy
        """
        text = ""
        
        try:
            # Method 1: Try PyMuPDF (fitz) - usually better for text extraction
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            
            if text.strip():
                return text.strip()
                
        except Exception as e:
            print(f"PyMuPDF extraction failed for {pdf_path}: {str(e)}")
        
        try:
            # Method 2: Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
                    
            if text.strip():
                return text.strip()
                
        except Exception as e:
            print(f"PyPDF2 extraction failed for {pdf_path}: {str(e)}")
        
        # Method 3: OCR fallback (if PDF is image-based)
        try:
            print(f"Attempting OCR for {pdf_path}...")
            doc = fitz.open(pdf_path)
            ocr_text = ""
            for page_num in range(min(3, len(doc))):  # Limit to first 3 pages for performance
                page = doc[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image for OCR
                from io import BytesIO
                img = Image.open(BytesIO(img_data))
                page_text = pytesseract.image_to_string(img)
                ocr_text += page_text + "\n"
            
            doc.close()
            return ocr_text.strip() if ocr_text.strip() else "No text could be extracted"
            
        except Exception as e:
            print(f"OCR extraction failed for {pdf_path}: {str(e)}")
            return "No text could be extracted"
    
    def analyze_content_with_gpt(self, pdf_contents):
        """
        Use GPT to analyze PDF contents and suggest groupings
        """
        if not self.client:
            print("❌ OpenAI client not initialized. Cannot perform content analysis.")
            return None
            
        # Prepare content summary for GPT
        content_summary = []
        for filename, text in pdf_contents.items():
            # Truncate text to avoid token limits
            truncated_text = text[:2000] if len(text) > 2000 else text
            content_summary.append({
                "filename": filename,
                "content": truncated_text
            })
        
        prompt = f"""
        Analyze the following PDF documents and group them ONLY when they have STRONG, SPECIFIC relationships with each other.
        Do NOT create generic groups. Only group documents that are clearly related through specific connections.
        
        Documents to analyze:
        {json.dumps(content_summary, indent=2)}
        
        Please provide a JSON response with the following structure:
        {{
            "groups": [
                {{
                    "group_name": "descriptive_name_for_group",
                    "description": "brief description of what these documents have in common",
                    "files": ["filename1.pdf", "filename2.pdf"]
                }}
            ]
        }}
        
        STRICT GROUPING CRITERIA - Only group documents if they have:
        1. **Same order/transaction ID** - Documents referencing the same specific order, invoice number, or transaction
        2. **Same project/case** - Documents belonging to the same specific project, case number, or work item
        3. **Sequential documents** - Parts of the same process (e.g., quote → invoice → receipt for same item)
        4. **Same entity with specific relationship** - Multiple documents from/about the same company/person for the same specific matter
        5. **Same event/date range** - Documents specifically related to the same event, meeting, or time period
        
        AVOID GENERIC GROUPINGS:
        - Do NOT group just because documents are "invoices" or "contracts" in general
        - Do NOT group just because they're from the same company unless they relate to the same specific matter
        - Do NOT group just because they're the same document type
        - Do NOT create broad categories like "financial documents" or "legal documents"
        
        IMPORTANT RULES:
        - Each document should belong to exactly one group
        - If documents don't have SPECIFIC relationships, place them in "not_related" 
        - Group names should reflect the SPECIFIC connection (e.g., "Order_12345_Documents", "ProjectABC_Contract_Series", "Meeting_2024_Jan_Materials")
        - Be conservative - when in doubt, put documents in "not_related" rather than forcing weak groupings
        - Minimum 2 documents per group (except "not_related")
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document analysis expert. Analyze documents and group them logically based on content similarity."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    print("❌ Could not parse GPT response as JSON")
                    return None
                    
        except Exception as e:
            print(f"❌ Error calling GPT API: {str(e)}")
            return None
    
    def create_grouped_folders(self, grouping_result):
        """
        Create folders and move PDFs based on GPT analysis
        """
        if not grouping_result or 'groups' not in grouping_result:
            print("❌ Invalid grouping result")
            return False
        
        # Create base output directory
        Path(self.output_base_dir).mkdir(exist_ok=True)
        
        moved_files = 0
        total_groups = len(grouping_result['groups'])
        
        print(f"\n📁 Creating {total_groups} groups...")
        
        for i, group in enumerate(grouping_result['groups'], 1):
            group_name = group.get('group_name', f'group_{i}')
            description = group.get('description', 'No description')
            files = group.get('files', [])
            
            # Sanitize folder name
            safe_group_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            group_folder = os.path.join(self.output_base_dir, safe_group_name)
            
            # Create group folder
            Path(group_folder).mkdir(exist_ok=True)
            
            # Create description file
            desc_file = os.path.join(group_folder, "group_description.txt")
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(f"Group: {group_name}\n")
                f.write(f"Description: {description}\n")
                f.write(f"Files: {len(files)}\n\n")
                f.write("Files in this group:\n")
                for file in files:
                    f.write(f"- {file}\n")
            
            # Special handling for not_related group
            if group_name.lower() == "not_related":
                print(f"\n📂 Group {i}: {group_name} 🔍")
                print(f"   📝 {description}")
                print(f"   📄 Unrelated files: {len(files)}")
            else:
                print(f"\n📂 Group {i}: {group_name}")
                print(f"   📝 {description}")
                print(f"   📄 Files: {len(files)}")
            
            # Move files to group folder
            for filename in files:
                source_path = os.path.join(self.input_dir, filename)
                dest_path = os.path.join(group_folder, filename)
                
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, dest_path)
                        if group_name.lower() == "not_related":
                            print(f"   ✓ Moved unrelated file: {filename}")
                        else:
                            print(f"   ✓ Moved: {filename}")
                        moved_files += 1
                    except Exception as e:
                        print(f"   ❌ Failed to move {filename}: {str(e)}")
                else:
                    print(f"   ⚠️  File not found: {filename}")
        
        print(f"\n✅ Successfully moved {moved_files} files into {total_groups} groups")
        return True
    
    def process_pdfs(self):
        """
        Main method to process all PDFs and group them
        """
        if not os.path.exists(self.input_dir):
            print(f"❌ Input directory '{self.input_dir}' not found")
            return False
        
        # Get all PDF files
        pdf_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith('.pdf'):
                pdf_files.append(filename)
        
        if not pdf_files:
            print(f"❌ No PDF files found in '{self.input_dir}'")
            return False
        
        print("🔍 PDF CONTENT ANALYSIS & GROUPING")
        print("=" * 50)
        print(f"📁 Input directory: {self.input_dir}")
        print(f"📁 Output directory: {self.output_base_dir}")
        print(f"📄 Found {len(pdf_files)} PDF files")
        print("-" * 50)
        
        # Extract text from all PDFs
        pdf_contents = {}
        print("\n📖 Extracting text from PDFs...")
        
        for i, filename in enumerate(pdf_files, 1):
            print(f"   {i}/{len(pdf_files)}: {filename}")
            pdf_path = os.path.join(self.input_dir, filename)
            text = self.extract_text_from_pdf(pdf_path)
            pdf_contents[filename] = text
            
            # Show preview of extracted text
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"      Preview: {preview}")
        
        print(f"\n✅ Text extraction complete for {len(pdf_contents)} files")
        
        # Analyze with GPT
        print("\n🤖 Analyzing content with GPT...")
        grouping_result = self.analyze_content_with_gpt(pdf_contents)
        
        if not grouping_result:
            print("❌ GPT analysis failed")
            return False
        
        print("✅ GPT analysis complete")
        
        # Create grouped folders
        print("\n📁 Creating grouped folders...")
        success = self.create_grouped_folders(grouping_result)
        
        if success:
            print(f"\n🎉 PDF grouping complete!")
            print(f"📁 Check the '{self.output_base_dir}' directory for grouped PDFs")
            print("💡 Each group folder contains a 'group_description.txt' file explaining the grouping logic")
        
        return success

def main():
    """
    Main function to run PDF grouping
    """
    print("🚀 Starting PDF Grouping with LLM Analysis...")
    print("\n⚠️  Requirements:")
    print("   - OpenAI API key (set OPENAI_API_KEY environment variable)")
    print("   - pip install openai PyPDF2 pytesseract PyMuPDF pillow")
    print("   - Tesseract OCR installed (for image-based PDFs)")
    
    # Initialize grouper
    grouper = PDFGrouper()
    
    if not grouper.client:
        print("\n❌ Cannot proceed without OpenAI API key")
        print("💡 Set your API key: export OPENAI_API_KEY='your-key-here'")
        return False
    
    # Process PDFs
    return grouper.process_pdfs()

if __name__ == "__main__":
    main()
