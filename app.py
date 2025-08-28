from flask import Flask, render_template, request, jsonify
from scrapers.scrape_fanfiction import scrapeFanfiction
from scrapers.scrape_general import scrapeGeneral
from scrapers.scrape_ao3 import scrapeAO3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])    
def index():
    if request.method == 'POST':
        siteChoice = request.form['site']
        storyUrl = request.form['url']
        dirName = request.form['dirName']

        print(f"Site selected: {siteChoice}")
        print(f"URL entered: {storyUrl}")
        print(f"Directory name entered: {dirName}")

        if siteChoice == 'fanfiction':
            print("Starting FanFiction.net scraper...")
            scrapeFanfiction(storyUrl, dirName)
        elif siteChoice == 'ao3':
            print("Starting ArchiveOfOurOwn.org scraper...")
            scrapeAO3(storyUrl, dirName)
        elif siteChoice == 'general':
            print("Starting general scraper...")
            scrapeGeneral(storyUrl, dirName)

        return jsonify({
            'status': 'success', 
            'message': 'Process completed successfully! Check console.'
        })

    return render_template('frontEnd.html')

@app.route('/log_selection', methods=['POST'])
def log_selection():
    data = request.get_json()
    site = data.get('site')
    if site:
        print(f"User selected: {site}")
    return jsonify({'status': 'logged'})

if __name__ == '__main__':
    app.run(debug=True)