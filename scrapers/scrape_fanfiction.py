from bs4 import BeautifulSoup
import pdfkit
import os
import time
from pypdf import PdfWriter
import undetected_chromedriver as uc

CONFIG = {
    'pdfkitConfig': pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"),
    'maxRetries': 3,
    'retryDelay': 5,
    'pdfkitOptions': {
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
    'pauseBetweenChapters': 2
}

def getStoryInfo(driver, firstChapterUrl):
    print(f"Fetching story information from: {firstChapterUrl}")
    driver.get(firstChapterUrl)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        lastChapterOption = soup.select('select#chap_select option')[-1]
        totalChapters = int(lastChapterOption.get('value'))
        print(f"Found a total of {totalChapters} chapters.")
    except IndexError:
        print("Could not find chapter dropdown. Assuming one-shot.")
        totalChapters = 1
    return totalChapters

def convertChaptersToPDF(driver, chapterUrl, outputPath, chapterNum):
    for attempt in range(CONFIG['maxRetries']):
        try:
            print(f"\nLoading {chapterUrl} in browser (Chapter {chapterNum}, Attempt {attempt + 1})...")
            driver.get(chapterUrl)
            time.sleep(7)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            storyContentDiv = soup.find('div', id='storytext')
            
            if not storyContentDiv:
                raise Exception("Could not find story content div ('div#storytext').")
            
            htmlBody = str(storyContentDiv)
            cleanHtml = f"""
            <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Chapter {chapterNum}</title>
            <style>
                body {{ font-family: Georgia, serif; font-size: 1.2em; line-height: 1.6; margin: 2em; max-width: 800px; }}
                p {{ margin-bottom: 1em; }} hr {{ display: none; }}
            </style></head><body><h1>Chapter {chapterNum}</h1>{htmlBody}</body></html>
            """

            print(f"Converting content to PDF...")
            pdfkit.from_string(cleanHtml, outputPath, configuration=CONFIG['pdfkitConfig'])
            print(f"Successfully created {outputPath}")
            return True
        except OSError as oe:
            print(f"!!! PDFKIT ERROR on chapter {chapterNum}: {oe}")
            return False
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for chapter {chapterNum}: {e}")
            if attempt < CONFIG['maxRetries'] - 1:
                print(f"Waiting {CONFIG['retryDelay']} seconds before retrying...")
                time.sleep(CONFIG['retryDelay'])
            else:
                print(f"All attempts failed for chapter {chapterNum}. Moving on.")
                return False

def mergeAndCleanup(pdfFiles, outputDir, finalFilenameBase):
    if not pdfFiles:
        print("\nNo PDFs were created to merge.")
        return
    print("\n--- Starting Merge Process ---")
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

def scrapeFanfiction(firstChapterUrl, dirName):
    if not firstChapterUrl.startswith(('http://', 'https://')):
        firstChapterUrl = 'https://' + firstChapterUrl

    print("Initializing automated browser...")

    options = uc.ChromeOptions()
    profilePath = r"C:\Users\shubh\AppData\Local\Google\Chrome\User Data\Default"
    options.add_argument(f"--user-data-dir={profilePath}")
    options.add_argument("--start-minimized")

    driver = uc.Chrome(options=options)

    try:
        totalChapters = getStoryInfo(driver, firstChapterUrl)
    except Exception as e:
        print(f"Error: Could not fetch initial story page. {e}")
        driver.quit()
        return

    os.makedirs(dirName, exist_ok=True)
    createdPDFFiles = []
    urlParts = firstChapterUrl.split('/')
    
    for chapterNum in range(1, totalChapters + 1):
        if chapterNum > 1:
            urlParts[5] = str(chapterNum)
            chapterUrl = '/'.join(urlParts)
        else:
            chapterUrl = firstChapterUrl
        
        outputPath = os.path.join(dirName, f"Chapter_{chapterNum}.pdf")

        if convertChaptersToPDF(driver, chapterUrl, outputPath, chapterNum):
            createdPDFFiles.append(outputPath)
            print(f"Pausing for {CONFIG['pauseBetweenChapters']} seconds...")
            time.sleep(CONFIG['pauseBetweenChapters'])

    driver.quit()
    mergeAndCleanup(createdPDFFiles, dirName, os.path.basename(dirName))