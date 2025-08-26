from flask import Flask, render_template, request
# Imagine your existing scrapers are refactored into these functions
# from scrapers import scrape_fanfiction, scrape_ao3 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get data from the form
        site_choice = request.form['site']
        story_url = request.form['url']
        
        print(f"Site selected: {site_choice}")
        print(f"URL entered: {story_url}")
        
        # --- This is the core logic ---
        if site_choice == 'fanfiction':
            print("Starting FanFiction.net scraper...")
            # scrape_fanfiction(story_url) # You would call your actual function here
        elif site_choice == 'ao3':
            print("Starting ArchiveOfOurOwn.org scraper...")
            # scrape_ao3(story_url) # You would call the AO3-specific function here
        elif site_choice == 'general':
            print("Starting general scraper...")
            # scrape_general(story_url) # You would call the general function here

        return "Scraping process started! Check the console for progress."

    # For a GET request, just show the page
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)