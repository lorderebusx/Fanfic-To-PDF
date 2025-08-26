from flask import Flask, render_template, request
from scrapers.scrape_fanfiction import scrape_fanfiction

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get data from the form
        siteChoice = request.form['site']
        storyUrl = request.form['url']
        dirName = request.form['dirname']

        print(f"Site selected: {siteChoice}")
        print(f"URL entered: {storyUrl}")
        print(f"Directory name entered: {dirName}")

        # --- This is the core logic ---
        if siteChoice == 'fanfiction':
            print("Starting FanFiction.net scraper...")
            scrape_fanfiction(storyUrl, dirName) # You would call your actual function here
        elif siteChoice == 'ao3':
            print("Starting ArchiveOfOurOwn.org scraper...")
            # scrape_ao3(story_url) # You would call the AO3-specific function here
        elif siteChoice == 'general':
            print("Starting general scraper...")
            # scrape_general(story_url) # You would call the general function here

        return "Scraping process started! Check the console for progress."

    # For a GET request, just show the page
    return render_template('frontEnd.html')

if __name__ == '__main__':
    app.run(debug=True)