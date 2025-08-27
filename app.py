from flask import Flask, render_template, request, jsonify
from scrapers.scrape_fanfiction import scrapeFanfiction
from scrapers.scrape_general import scrapeGeneral

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])    
def index():
    if request.method == 'POST':
        # Get data from the form
        siteChoice = request.form['site']
        storyUrl = request.form['url']
        dirName = request.form['dirName']

        print(f"Site selected: {siteChoice}")
        print(f"URL entered: {storyUrl}")
        print(f"Directory name entered: {dirName}")

        # --- This is the core logic ---
        if siteChoice == 'fanfiction':
            print("Starting FanFiction.net scraper...")
            scrapeFanfiction(storyUrl, dirName) # You would call your actual function here
        elif siteChoice == 'ao3':
            print("Starting ArchiveOfOurOwn.org scraper...")
            # scrape_ao3(story_url) # You would call the AO3-specific function here
        elif siteChoice == 'general':
            print("Starting general scraper...")
            scrapeGeneral(storyUrl, dirName)

        return jsonify({
            'status': 'success', 
            'message': 'Process completed successfully! Check console.'
        })

    # For a GET request, just show the page
    return render_template('frontEnd.html')

if __name__ == '__main__':
    app.run(debug=True)