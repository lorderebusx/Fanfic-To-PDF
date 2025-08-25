import pdfkit
import os
import time

config = pdfkit.configuration(wkhtmltopdf= "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

options = {
    '--user-style-sheet': 'style.css',
    '--disable-plugins': '',
    '--disable-smart-shrinking': '',
    '--javascript-delay': '3000',  # Wait 1000ms for JavaScript to finish
    '--no-stop-slow-scripts': '',
    '--load-error-handling': 'skip', # Skip content that fails to load
    '--quiet': '' # Suppresses console output from wkhtmltopdf
}




input_url = input("Please enter the url w/o chapter number: ")
chapterRange = int(input("Please enter the chapter range (e.g., 10 for chapters 1-10): "))

dirName = input("Please enter the directory name to save the PDFs: ")

outputDir = dirName
os.makedirs(outputDir, exist_ok=True)

for i in range(1, chapterRange + 1):
    try:
        print(f"\nDEBUG: Loop starting for i = {i}")

        url = f"{input_url}{i}"

        print(f"DEBUG: Generated URL is: {url}")

        fileName = f"Chapter {i}.pdf"
        outputPath = os.path.join(outputDir, fileName)

        print(f"Converting {url} to {outputPath}...")

        pdfkit.from_url(url, outputPath, configuration=config, options=options)

        print(f"Successfully created {outputPath}")

    except:
        break

