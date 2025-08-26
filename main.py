import requests
from bs4 import BeautifulSoup
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

indexURL = input("Please enter the URL of the index/table of contents: ")
linkSelector = "div.entry-content a"
dirName = input("Please enter the directory name to save the PDFs: ")

if not indexURL.startswith(('http://', 'https://')):
    indexURL = 'https://' + indexURL

print(f"\nFetching index page: {indexURL}")
response = requests.get(indexURL)
soup = BeautifulSoup(response.content, 'html.parser')

chapterLinks = [a['href'] for a in soup.select(linkSelector) if a.has_attr('href')]

if not chapterLinks:
    print("No chapter links found.")
    exit()

print(f"Found {len(chapterLinks)} chapter links. Starting PDF conversion...")

outputDir = dirName
os.makedirs(outputDir, exist_ok=True)

created_files = []

for i, link in enumerate(chapterLinks):

    success = False
    chapterNum = i + 1

    for attempt in range(MAX_RETRIES):
        try:
            chapterURL = link
            fileName = f"Chapter {chapterNum}.pdf"
            outputPath = os.path.join(outputDir, fileName)

            print(f"\nConverting {chapterURL} --- Attempt {attempt + 1} of {MAX_RETRIES}")
            pdfkit.from_url(chapterURL, outputPath, configuration=config, options=options)
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
                print(f"All attempts failed for chapter {chapterNum}.")
    
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
