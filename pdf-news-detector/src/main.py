from azure_utils.storage import AzureStorageService
import os
from pdf.reader import extract_content
from analysis.text_analyzer import analyze_text
from analysis.image_analyzer import analyze_image
from analysis.coherence_analyzer import analyze_coherence
from report.generator import generate_report

def main():
    # Initialize Azure Storage Service
    storage_service = AzureStorageService("zetianyuhackathonsa")
    container_name = "training-picture"
    
    # Find all PDF files in the container
    pdf_blobs = storage_service.find_pdf_files(container_name)
    
    if not pdf_blobs:
        print("No PDF files found in the container.")
        return
    
    print(f"Found {len(pdf_blobs)} PDF file(s): {pdf_blobs}")
    
    # Process each PDF file
    for blob_name in pdf_blobs:
        print(f"\nProcessing: {blob_name}")
        
        pdf_path = f"./{blob_name}"
        
        try:
            # Download PDF from Azure Blob Storage
            storage_service.download_blob(container_name, blob_name, pdf_path)
            
            # Extract content from the PDF
            text, images = extract_content(pdf_path)
            
            # Analyze text and images
            text_score, text_details = analyze_text(text)
            image_results = [analyze_image(image) for image in images]
            
            # Analyze coherence between text and images
            coherence_score, coherence_details = analyze_coherence(text, images)
            
            # Extract image scores and details
            if image_results:
                image_scores = [result[0] for result in image_results]
                image_details_list = [result[1] for result in image_results]
                image_score = sum(image_scores) / len(image_scores)
                # Combine all image analysis details
                image_details = {
                    "average_score": image_score,
                    "individual_analyses": image_details_list,
                    "total_images": len(image_results)
                }
            else:
                image_score = 0
                image_details = {"message": "No images found in PDF", "total_images": 0}
            
            # Generate report with detailed analysis
            report = generate_report(
                image_score=image_score, 
                text_score=text_score, 
                coherence_score=coherence_score,
                pdf_name=blob_name,
                image_details=image_details,
                text_details=text_details,
                coherence_details=coherence_details
            )
            
            print(f"Report generated for {blob_name}:", report)
            
        except Exception as e:
            print(f"Error processing {blob_name}: {str(e)}")
        
        finally:
            # Clean up the downloaded PDF
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

if __name__ == "__main__":
    main()