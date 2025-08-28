import pdfkit
import os
import time
from urllib.parse import urlparse, urlunparse

# Re-using the same configuration dictionary structure
CONFIG = {
    'pdfkitConfig': pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"),
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
    'maxRetries': 3,
    'retryDelay': 5
}

def scrapeAO3(workURL, dirName):
    """Downloads an entire work from Archive of Our Own (AO3) as a single PDF."""
    if not workURL.startswith(('http://', 'https://')):
        workURL = 'https://' + workURL

    # Construct the URL to view the entire work on one page
    parsedUrl = urlparse(workURL)
    # Rebuild the URL without any queries or fragments, keeping only the core path
    cleanUrlPath = parsedUrl.path
    fullWorkUrl = urlunparse((parsedUrl.scheme, parsedUrl.netloc, cleanUrlPath, '', 'view_full_work=true', ''))

    print(f"Fetching the entire work from: {fullWorkUrl}")

    os.makedirs(dirName, exist_ok=True)
    # The output file will just be the directory name with a .pdf extension
    outputPath = os.path.join(dirName, f"{os.path.basename(dirName)}.pdf")

    for attempt in range(CONFIG['maxRetries']):
        try:
            print(f"Converting to PDF (Attempt {attempt + 1} of {CONFIG['maxRetries']})...")
            # We can use from_url directly since AO3 is less restrictive than FF.net
            pdfkit.from_url(fullWorkUrl, outputPath, configuration=CONFIG['pdfkitConfig'])
            print(f"Successfully created book at: {outputPath}")
            return # Exit the function on success
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < CONFIG['maxRetries'] - 1:
                print(f"Retrying in {CONFIG['retryDelay']} seconds...")
                time.sleep(CONFIG['retryDelay'])
            else:
                print("All attempts failed. Could not download the work.")