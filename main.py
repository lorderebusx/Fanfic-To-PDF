import pdfkit
import os
import time
from pypdf import PdfWriter

config = pdfkit.configuration(wkhtmltopdf= "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

options = {
    '--user-style-sheet': 'style.css',
    '--disable-plugins': '',
    '--disable-smart-shrinking': '',
    '--javascript-delay': '3000',
    '--no-stop-slow-scripts': '',
    '--load-error-handling': 'skip',
    '--quiet': ''
}

MAX_RETRIES = 3
RETRY_DELAY = 5

input_url = input("Please enter the url w/o chapter number: ")
chapterRange = int(input("Please enter the chapter range (e.g., 10 for chapters 1-10): "))
dirName = input("Please enter the directory name to save the PDFs: ")

outputDir = dirName
os.makedirs(outputDir, exist_ok=True)

created_files = []

for i in range(1, chapterRange + 1):

    success = False

    for attempt in range(MAX_RETRIES):
        try:
            print(f"\nDEBUG: Loop starting for i = {i}")

            url = f"{input_url}{i}"
            print(f"DEBUG: Generated URL is: {url}")

            fileName = f"Chapter {i}.pdf"
            outputPath = os.path.join(outputDir, fileName)

            print(f"\nConverting {url} --- Attempt {attempt + 1} of {MAX_RETRIES}")
            pdfkit.from_url(url, outputPath, configuration=config, options=options)
            print(f"Successfully created {outputPath}")

            created_files.append(outputPath)

            success = True
            break            

        except Exception as e:

            print(f"\n\nAttempt {attempt + 1} failed for chapter {i}: {e}")

            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"All attempts failed for chapter {i}.")
    
    if success:
        print("\nPausing for 2 seconds...")
        time.sleep(2)

if created_files:
    print(f"\n--- Starting Merge Process ---")

    merger = PdfWriter()

    for pdf in created_files:
        print(f"Merging {pdf}...")
        merger.append(pdf)

    baseFileName = os.path.basename(dirName)

    merged_output_path = os.path.join(outputDir, f"{baseFileName}.pdf")

    print(f"\nWriting merged PDF to {merged_output_path}...")
    merger.write(merged_output_path)
    merger.close()

    print(f"\n--- Merging process complete! ---")
    time.sleep(0.2)
    print(f"--- Beginning clean-up ---")

    for pdf in created_files:
        os.remove(pdf)

    print(f"\n--- Clean-up complete! ---")
else:
    print("\nNo files were created, so no merging was performed.")
