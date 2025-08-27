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
        '--user-style-sheet': 'static/style.css',
        '--page-size': 'Letter',
        '--margin-top': '0.75in',
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
    time.sleep(3) 
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
            
            baseTag = soup.new_tag('base', href=chapterURL)
            if soup.head:
                soup.head.insert(0, baseTag)

            for s in soup.select('script'):
                s.decompose()
            
            htmlContent = str(soup)

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
                return False



def mergeAndCleanup(pdfFiles, outputDir, finalFilenameBase):
    if not pdfFiles:
        print("\nNo PDFs were created to merge.")
        return

    print(f"\n--- Starting Merge Process ---")
    merger = PdfWriter()
    for pdfPath in pdfFiles:
        merger.append(pdfPath)

    finalBookPath = os.path.join(outputDir, f"{finalFilenameBase}.pdf")
    print(f"Writing merged PDF to {finalBookPath}...")
    merger.write(finalBookPath)
    merger.close()
    
    print("\n--- Merging process complete! Cleaning up... ---")
    for pdfPath in pdfFiles:
        os.remove(pdfPath)
    
    print(f"Script finished. Your merged book is ready at: {finalBookPath}")

def scrapeFanfiction(firstChapterURL, dirName):

    if not firstChapterURL.startswith(('http://', 'https://')):
        firstChapterURL = 'https://' + firstChapterURL

    #session = requests.Session()

    print("Initializing automated browser...")

    options = webdriver.ChromeOptions()
    profilePath = r"C:\Users\shubh\AppData\Local\Google\Chrome\User Data\Default"
    options.add_argument(f"user-data-dir={profilePath}")
    options.add_argument("start-minimized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')

    #driverPath = os.path.join(os.getcwd(), 'chromedriver.exe')
    service = webdriver.ChromeService(executablePath = ChromeDriverManager().install())
    driver = webdriver.Chrome(service = service, options = options)

    stealth(driver,
            languages = ["en-US", "en"],
            vendor = "Google Inc.",
            platform = "Win32",
            webgl_vendor = "Intel Inc.",
            renderer = "Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    
    driver = uc.Chrome()

    try:
        totalChapters = getStoryInfo(driver, firstChapterURL)
    except Exception as e:
        print(f"Error: Could not fetch initial story page. {e}")
        driver.quit()
        return

    os.makedirs(dirName, exist_ok=True)
    createdPDFfiles = []
    urlParts = firstChapterURL.split('/')
    
    for chapterNum in range(1, totalChapters + 1):
        urlParts[5] = str(chapterNum)
        chapterURL = '/'.join(urlParts)
        
        outputPath = os.path.join(dirName, f"Chapter_{chapterNum}.pdf")

        if convertChaptersToPDF(driver, chapterURL, outputPath, chapterNum, CONFIG):
            createdPDFfiles.append(outputPath)
            print(f"Pausing for {CONFIG['pause_between_chapters']} seconds...")
            time.sleep(CONFIG['pause_between_chapters'])

    driver.quit
    mergeAndCleanup(createdPDFfiles, dirName, os.path.basename(dirName))
