import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import time
from pypdf import PdfWriter
from os.path import commonprefix

CONFIG = {
    'pdfkitConfig': pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"),
    'pdfkitOptions': {
        '--user-style-sheet': 'static/style.css',
        '--disable-plugins': '',
        '--disable-smart-shrinking': '',
        '--javascript-delay': '3000',
        '--no-stop-slow-scripts': '',
        '--load-error-handling': 'skip',
        '--quiet': ''
    },
    'maxRetries': 3,
    'retryDelay': 5,
    'pauseBetweenChapters': 2
}

def findLinkPattern(links):
    if not links:
        return ""
    pattern = commonprefix(links)
    if '/' in pattern:
        pattern = pattern[:pattern.rfind('/')+1]
    return pattern

def scrapeGeneral(indexURL, dirName):
    """Scrapes a series of links from a general index page."""
    if not indexURL.startswith(('http://', 'https://')):
        indexURL = 'https://' + indexURL

    print(f"\nFetching index page: {indexURL}")
    response = requests.get(indexURL)
    soup = BeautifulSoup(response.content, 'html.parser')

    generalSelector = "div.entry-content a"
    linkTags = soup.select(generalSelector)
    hrefs = [tag['href'] for tag in linkTags if tag.has_attr('href')]

    linkPattern = findLinkPattern(hrefs)
    if not linkPattern:
        print("Could not determine a common link pattern. Exiting.")
        return

    print(f"Determined link pattern: {linkPattern}")
    excludeKeywords = ['?share=', 'twitter', 'facebook', 'reddit']
    chapterLinks = [href for href in hrefs if href.startswith(linkPattern) and not any(keyword in href for keyword in excludeKeywords)]

    if not chapterLinks:
        print("No chapter links found matching the pattern.")
        return

    print(f"Found {len(chapterLinks)} chapter links. Starting PDF conversion...")
    os.makedirs(dirName, exist_ok=True)
    createdFiles = []

    for i, link in enumerate(chapterLinks):
        success = False
        chapterNum = i + 1
        for attempt in range(CONFIG['maxRetries']):
            try:
                chapterURL = link
                fileName = f"Chapter_{chapterNum}.pdf"
                outputPath = os.path.join(dirName, fileName)
                print(f"\nConverting {chapterURL} (Attempt {attempt + 1})...")
                pdfkit.from_url(chapterURL, outputPath, configuration=CONFIG['pdfkitConfig'], options=CONFIG['pdfkitOptions'])
                print(f"Successfully created {outputPath}")
                createdFiles.append(outputPath)
                success = True
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for chapter {chapterNum}: {e}")
                if attempt < CONFIG['maxRetries'] - 1:
                    print(f"Retrying in {CONFIG['retryDelay']} seconds...")
                    time.sleep(CONFIG['retryDelay'])
                else:
                    print(f"All attempts failed for chapter {chapterNum}.")
        
        if success:
            print(f"Pausing for {CONFIG['pauseBetweenChapters']} seconds...")
            time.sleep(CONFIG['pauseBetweenChapters'])

    if createdFiles:
        print("\n--- Starting Merge Process ---")
        merger = PdfWriter()
        for pdf in createdFiles:
            merger.append(pdf)
        baseFileName = os.path.basename(dirName)
        mergedOutputPath = os.path.join(dirName, f"{baseFileName}.pdf")
        print(f"Writing merged PDF to {mergedOutputPath}...")
        merger.write(mergedOutputPath)
        merger.close()
        print("\n--- Merging process complete! Cleaning up... ---")
        for pdf in createdFiles:
            os.remove(pdf)
        print(f"Script finished. Your merged book is at: {mergedOutputPath}")
    else:
        print("\nScript finished, but no PDFs were created to merge.")