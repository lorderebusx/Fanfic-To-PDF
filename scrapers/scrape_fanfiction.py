#import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import time
from pypdf import PdfWriter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import undetected_chromedriver as uc

CONFIG = {
    'pdfkit_config': pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"),
    'max_retries': 3,
    'retry_delay': 5,
    'pdfkit_options': {
        '--user-style-sheet': 'style.css',
        '--page-size': 'Letter',         # NEW: Set a standard page size
        '--margin-top': '0.75in',        # NEW: Add some margins for a book-like feel
        '--margin-right': '0.75in',
        '--margin-bottom': '0.75in',
        '--margin-left': '0.75in',
        '--disable-javascript': '',
        '--viewport-size': '1920x1080',
        '--disable-plugins': '',
        '--disable-smart-shrinking': '',
        '--load-error-handling': 'skip',
        '--quiet': ''
    },
    'pause_between_chapters': 2
}

def getStoryInfo(driver, firstChapterURL):

    print(f"Fetching story information from: {firstChapterURL}")
    driver.get(firstChapterURL)
    time.sleep(3) # Wait for page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        lastChapterOption = soup.select('select#chap_select option')[-1]
        totalChapters = int(lastChapterOption.get('value'))
        print(f"Found a total of {totalChapters} chapters.")

    except IndexError:
        print(f"Could not find chapter dropdown. Assuming one-shot.")
        totalChapters = 1

    return totalChapters

def convertChaptersToPDF(driver, chapterURL, outputPath, chapterNum, CONFIG):
    for attempt in range(CONFIG['max_retries']):
        try:
            print(f"\nLoading {chapterURL} in browser (Chapter {chapterNum}, Attempt {attempt + 1})...")
            driver.get(chapterURL)
            time.sleep(7)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            for s in soup.select('script, style, link[rel="stylesheet"]'):
                s.decompose()
            
            # 1. Add a <base> tag to resolve relative URLs
            base_tag = soup.new_tag('base', href=chapterURL)
            if soup.head:
                soup.head.insert(0, base_tag)
            
            htmlContent = str(soup)

            #htmlContent = driver.page_source

            print(f"\nConverting {chapterURL} (Chapter {chapterNum}, Attempt {attempt + 1})...")
            pdfkit.from_string(htmlContent, outputPath, configuration=CONFIG['pdfkit_config'], options=CONFIG['pdfkit_options'])
            print(f"Successfully created {outputPath}")
            return True
        
        except OSError as oe:
            print(f"!!! PDFKIT ERROR on chapter {chapterNum}: {oe}")
            return False
        
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

    if not first_chapter_url.startswith(('http://', 'https://')):
        first_chapter_url = 'https://' + first_chapter_url

    #session = requests.Session()

    print("Initializing automated browser...")

    options = webdriver.ChromeOptions()
    profilePath = r"C:\Users\shubh\AppData\Local\Google\Chrome\User Data\Default"
    options.add_argument(f"user-data-dir={profilePath}")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')

    #driverPath = os.path.join(os.getcwd(), 'chromedriver.exe')
    service = webdriver.ChromeService(executablePath = ChromeDriverManager().install())
    driver = webdriver.Chrome(service = service, options = options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    
    driver = uc.Chrome()

    try:
        total_chapters = getStoryInfo(driver, first_chapter_url)
    except Exception as e:
        print(f"Error: Could not fetch initial story page. {e}")
        driver.quit()
        return

    os.makedirs(dir_name, exist_ok=True)
    created_pdf_files = []
    url_parts = first_chapter_url.split('/')
    
    for chapter_num in range(1, total_chapters + 1):
        url_parts[5] = str(chapter_num)
        chapter_url = '/'.join(url_parts)
        
        output_path = os.path.join(dir_name, f"Chapter_{chapter_num}.pdf")

        if convertChaptersToPDF(driver, chapter_url, output_path, chapter_num, CONFIG):
            created_pdf_files.append(output_path)
            print(f"Pausing for {CONFIG['pause_between_chapters']} seconds...")
            time.sleep(CONFIG['pause_between_chapters'])

    driver.quit
    mergeAndCleanup(created_pdf_files, dir_name, os.path.basename(dir_name))
