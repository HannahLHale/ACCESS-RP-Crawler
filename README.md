# RP Documentation Web Crawler-
A web-based tool for crawling Resource Provider (RP) documentation sites and searching for specific keywords in user documentation pages.
## Notes
- The crawler respects the allowed_prefix for each rp to stay within documentation boundaries
- Crawling may take several minutes depending on the site size (Example: JETSTREAM has a large amount of documentation)
- Keyword Search: Search all crawled URLs for specific keywords
- Export Results: Download URLs and search results as CSV files

SETUP
1. Install dependencies
Make sure you have Python 3.7+ installed, then install the required packages:
**pip install -r requirements.txt**

2. File Structure
   
rpCrawler/ <br>
├── app.py                 
├── requirements.txt       
├── index.html            
└── README.md             
4. Start backend server
Run the Flask server:
**python app.py**
You should see output like:
# Running on http://0.0.0.0:5000

4. 
Open `index.html` in your browser. 
- Use a local web server (recommended)
**python -m http.server 8000**
# Then open http://localhost:8000

5. Check Connection
The interface should show "Server connected" with a green circle indicator. If it shows "Server not connected" message with a red circle indicator:
- Make sure `app.py` is running
- Check that the flask server is on port 5000

FUNCTIONALITY
### Step 1: Crawl documentation
1. Select a RP from the dropdown
2. Click "Start Crawling"
3. Wait for the crawl to finish
Optionally download the URLs as a .csv file

### Step 2: Search for keywords
1. Enter keywords (one per line) in the text box
2. Click "Search keywords"
3. Review the results showing which URLs contain keywords
Optionally download the results as a CSV file

## Available Resource Providers
- Bridges2
- ACES
- Anvil
- CloudBank
- Delta
- DeltaAI
- Derecho
- Expanse
- Granite
- Jetstream2
- KyRIC
- Launch
- Neocortex
- Ookami
- OSN
- OSG
- PNRP
- Ranch
- REPACSS
- Sage
- Stampede3

- Voyager

