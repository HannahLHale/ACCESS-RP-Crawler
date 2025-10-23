from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

app = Flask(__name__)
CORS(app)

# logging
logging.basicConfig(level=logging.INFO)

RP_DEFS = {
    'bridges2': {'url': 'https://www.psc.edu/resources/bridges-2/user-guide/', 'allowed_prefix': 'https://www.psc.edu/resources/bridges-2/user-guide/'},
    'aces': {'url': 'https://hprc.tamu.edu/kb/User-Guides/ACES/', 'allowed_prefix': 'https://hprc.tamu.edu/kb/User-Guides/ACES/'},
    'anvil': {'url': 'https://www.rcac.purdue.edu/anvil#docs', 'allowed_prefix': 'https://www.rcac.purdue.edu/anvil'},
    'cloudbank': {'url': 'https://www.cloudbank.org/training/', 'allowed_prefix': 'https://www.cloudbank.org/training/'},
    'delta': {'url': 'https://docs.ncsa.illinois.edu/systems/delta/en/latest/', 'allowed_prefix': 'https://docs.ncsa.illinois.edu/systems/delta/en/latest/'},
    'deltaai': {'url': 'https://docs.ncsa.illinois.edu/systems/deltaai/en/latest/', 'allowed_prefix': 'https://docs.ncsa.illinois.edu/systems/deltaai/en/latest/'},
    'derecho': {'url': 'https://arc.ucar.edu/docs', 'allowed_prefix': 'https://arc.ucar.edu/docs'},
    'expanse': {'url': 'https://www.sdsc.edu/systems/expanse/user_guide.html', 'allowed_prefix': 'https://www.sdsc.edu/systems/expanse/user_guide.html'},
    'granite': {'url': 'https://docs.ncsa.illinois.edu/systems/granite/en/latest/', 'allowed_prefix': 'https://docs.ncsa.illinois.edu/systems/granite/en/latest/'},
    'jetstream2': {'url': 'https://docs.jetstream-cloud.org/', 'allowed_prefix': 'https://docs.jetstream-cloud.org/'},
    'kyric': {'url': 'https://access-ci.atlassian.net/wiki/spaces/ACCESSdocumentation/pages/1214611459/KyRIC+-+Kentucky', 'allowed_prefix': 'https://access-ci.atlassian.net/wiki/spaces/ACCESSdocumentation/pages/1214611459/KyRIC+-+Kentucky'},
    'launch': {'url': 'https://hprc.tamu.edu/kb/User-Guides/Launch/', 'allowed_prefix': 'https://hprc.tamu.edu/kb/User-Guides/Launch/'},
    'neocortex': {'url': 'https://portal.neocortex.psc.edu/docs/', 'allowed_prefix': 'https://portal.neocortex.psc.edu/docs/'},
    'ookami': {'url': 'https://www.stonybrook.edu/commcms/ookami/support/faq/', 'allowed_prefix': 'https://www.stonybrook.edu/commcms/ookami/support/faq/'},
    'osn': {'url': 'https://openstoragenetwork.github.io/docs/', 'allowed_prefix': 'https://openstoragenetwork.github.io/docs/'},
    'osg': {'url': 'https://portal.osg-htc.org/documentation/', 'allowed_prefix': 'https://portal.osg-htc.org/documentation/'},
    'pnrp': {'url': 'https://nrp.ai/documentation/', 'allowed_prefix': 'https://nrp.ai/documentation/'},
    'ranch': {'url': 'https://docs.tacc.utexas.edu/hpc/ranch/', 'allowed_prefix': 'https://docs.tacc.utexas.edu/hpc/ranch/'},
    'repacss': {'url': 'https://guide.repacss.org/', 'allowed_prefix': 'https://guide.repacss.org/'},
    'sage': {'url': 'https://sagecontinuum.org/docs/', 'allowed_prefix': 'https://sagecontinuum.org/docs/'},
    'stampede3': {'url': 'https://docs.tacc.utexas.edu/hpc/stampede3/', 'allowed_prefix': 'https://docs.tacc.utexas.edu/hpc/stampede3/'},
    'voyager': {'url': 'https://www.sdsc.edu/systems/voyager/user_guide.html', 'allowed_prefix': 'https://www.sdsc.edu/systems/voyager/user_guide.html'},
}

class Crawler:
    def __init__(self, rp_name):
        if rp_name not in RP_DEFS:
            raise ValueError(f"Unknown RP name: {rp_name}")
        
        self.rp_name = rp_name
        self.visited_urls = []
        self.urls_to_visit = [RP_DEFS[rp_name]['url']]
        self.allowed_prefix = RP_DEFS[rp_name]['allowed_prefix']
        # default max_pages; can be overridden by caller
        self.max_pages = 700

    def download_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"Failed to download {url}: {e}")
            return None

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if not path:
                continue
            abs_url = urljoin(url, path)
            # Remove fragments
            abs_url = abs_url.split('#')[0]
            if abs_url.startswith(self.allowed_prefix):
                yield abs_url

    def add_url_to_visit(self, url):
        if (url and 
            url.startswith(self.allowed_prefix) and 
            url not in self.visited_urls and 
            url not in self.urls_to_visit):
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        if html:
            for linked_url in self.get_linked_urls(url, html):
                self.add_url_to_visit(linked_url)

    def run(self):
        while self.urls_to_visit and len(self.visited_urls) < self.max_pages:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception as e:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)
        
        return self.visited_urls


@app.route('/api/rp-list', methods=['GET'])
def get_rp_list():
    return jsonify({
        'rps': list(RP_DEFS.keys())
    })


@app.route('/api/crawl', methods=['POST'])
def crawl():
#Crawl an RP site and return URLs
    data = request.json
    logging.info(f'Received /api/crawl request: {data}')
    rp_name = data.get('rp_name')
    max_pages = data.get('max_pages', None)
    try:
        if max_pages is None:
            max_pages = 700
        else:
            max_pages = int(max_pages)
            if max_pages < 0:
                raise ValueError('max_pages must be >= 0')
    except Exception as e:
        return jsonify({'error': f'Invalid max_pages: {e}'}), 400
    
    if not rp_name:
        return jsonify({'error': 'rp_name is required'}), 400
    
    if rp_name not in RP_DEFS:
        return jsonify({'error': f'Unknown RP: {rp_name}'}), 400
    
    try:
        crawler = Crawler(rp_name)
        # treat 0 as no limit
        if max_pages == 0:
            crawler.max_pages = float('inf')
        else:
            crawler.max_pages = max_pages
        urls = crawler.run()
        
        return jsonify({
            'success': True,
            'rp_name': rp_name,
            'urls': urls,
            'count': len(urls)
        })
    except Exception as e:
        logging.exception('Crawl failed')
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
  #Search for keywords in URLs"""
    data = request.json
    urls = data.get('urls', [])
    keywords = data.get('keywords', [])
    
    if not urls:
        return jsonify({'error': 'urls list is required'}), 400
    
    if not keywords:
        return jsonify({'error': 'keywords list is required'}), 400
    
    # Convert keywords to lowercase for case-insensitive search
    keywords_lower = [k.lower() for k in keywords]
    
    results = []
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            found_keywords = [kw for kw in keywords if kw.lower() in page_text]
            
            if found_keywords:
                results.append({
                    'url': url,
                    'keywords': found_keywords
                })
                
        except Exception as e:
            logging.error(f"Could not access {url}: {e}")
    
    return jsonify({
        'success': True,
        'results': results,
        'count': len(results)
    })


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)