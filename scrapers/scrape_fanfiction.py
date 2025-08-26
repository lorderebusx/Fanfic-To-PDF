import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import time
from pypdf import PdfWriter

CONFIG = {
    'pdfkit.config' : pdfkit.configuration(wkhtmltopdf= "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"),
    'max_retries': 3,
    'retry_delay': 5,
    'pdfkit.options' : {
        '--user-style-sheet': 'style.css',
        '--disable-plugins': '',
        '--disable-smart-shrinking': '',
        '--javascript-delay': '3000',
        '--no-stop-slow-scripts': '',
        '--load-error-handling': 'skip',
        '--quiet': ''
    },
    'pause_between_chapters' : 2
}

def getStoryInfo(session, firstChapterURL):

    print(f"Fetching story information from: {firstChapterURL}")
    response = session.get(firstChapterURL)
    response.raise_for_status()  # Will raise an error for bad responses (4xx or 5xx)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        lastChapterOption = soup.select('select#chap_select option')[-1]
        totalChapters = int(lastChapterOption.get('value'))
        print(f"Found a total of {totalChapters} chapters.")

    except IndexError:
        print(f"Could not find chapter dropdown. Assuming one-shot.")
        totalChapters = 1

    return totalChapters

def convertChaptersToPDF(session, chapterURL, outputPath, chapterNum, CONFIG):
    for attempt in range(CONFIG['max_retries']):
        try:
            print(f"\nConverting {chapterURL} (Chapter {chapterNum}, Attempt {attempt + 1})...")
            pdfkit.from_url(chapterURL, outputPath, configuration=CONFIG['pdfkit_config'], options=CONFIG['pdfkit_options'])
            print(f"Successfully created {outputPath}")
            return True # Success
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for chapter {chapterNum}: {e}")
            if attempt < CONFIG['max_retries'] - 1:
                print(f"Waiting {CONFIG['retry_delay']} seconds before retrying...")
                time.sleep(CONFIG['retry_delay'])
            else:
                print(f"All attempts failed for chapter {chapterNum}. Moving on.")
                return False # Failure


def mergeAndCleanup(pdfFiles, outputDir, finalFilenameBase):
    if not pdfFiles:
        print("\nNo PDFs were created to merge.")
        return

    print(f"\n--- Starting Merge Process ---")
    merger = PdfWriter()
    for pdf_path in pdfFiles:
        merger.append(pdf_path)

    final_book_path = os.path.join(outputDir, f"{finalFilenameBase}.pdf")
    print(f"Writing merged PDF to {final_book_path}...")
    merger.write(final_book_path)
    merger.close()
    
    print("\n--- Merging process complete! Cleaning up... ---")
    for pdf_path in pdfFiles:
        os.remove(pdf_path)
    
    print(f"Script finished. Your merged book is ready at: {final_book_path}")

def scrape_fanfiction(first_chapter_url, dir_name):
    """Main function to scrape a full story from FanFiction.net."""
    if not first_chapter_url.startswith(('http://', 'https://')):
        first_chapter_url = 'https://' + first_chapter_url

    session = requests.Session()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    session.headers.update(headers)
    
    try:
        total_chapters = getStoryInfo(session, first_chapter_url)
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch initial story page. {e}")
        return

    os.makedirs(dir_name, exist_ok=True)
    created_pdf_files = []
    
    # Prepare the base URL for generating chapter links
    url_parts = first_chapter_url.split('/')
    
    for chapter_num in range(1, total_chapters + 1):
        url_parts[5] = str(chapter_num) # Chapter number is the 6th element (index 5)
        chapter_url = '/'.join(url_parts)
        
        output_path = os.path.join(dir_name, f"Chapter_{chapter_num}.pdf")

        if convertChaptersToPDF(session, chapter_url, output_path, chapter_num, CONFIG):
            created_pdf_files.append(output_path)
            print(f"Pausing for {CONFIG['pause_between_chapters']} seconds...")
            time.sleep(CONFIG['pause_between_chapters'])

    mergeAndCleanup(created_pdf_files, dir_name, os.path.basename(dir_name))
