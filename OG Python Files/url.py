import requests
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
#https://www.scrapingbee.com/blog/crawling-python/

BRIDGES2='https://www.psc.edu/resources/bridges-2/user-guide/'
ACES='https://hprc.tamu.edu/kb/User-Guides/ACES/'
ANVIL='https://www.rcac.purdue.edu/anvil#docs'
CLOUDBANK='https://www.cloudbank.org/training/'
DELTA='https://docs.ncsa.illinois.edu/systems/delta/en/latest/'
DELTAAI='https://docs.ncsa.illinois.edu/systems/deltaai/en/latest/'
DERECHO='https://arc.ucar.edu/docs'
EXPANSE='https://www.sdsc.edu/systems/expanse/user_guide.html'
GRANITE='https://docs.ncsa.illinois.edu/systems/granite/en/latest/'
JETSTREAM2='https://docs.jetstream-cloud.org/'
KYRIC='https://access-ci.atlassian.net/wiki/spaces/ACCESSdocumentation/pages/1214611459/KyRIC+-+Kentucky'
LAUNCH='https://hprc.tamu.edu/kb/User-Guides/Launch/'
NEOCORTEX='https://portal.neocortex.psc.edu/docs/'
OOKAMI='https://www.stonybrook.edu/commcms/ookami/support/faq/'
OSN='https://openstoragenetwork.github.io/docs/'
OSG='https://portal.osg-htc.org/documentation/'
PNRP='https://nrp.ai/documentation/'
RANCH='https://docs.tacc.utexas.edu/hpc/ranch/'
REPACSS='https://guide.repacss.org/'
SAGE='https://sagecontinuum.org/docs/'
STAMPEDE3='https://docs.tacc.utexas.edu/hpc/stampede3/'
VOYAGER='https://www.sdsc.edu/systems/voyager/user_guide.html'


RP_DEFS = {
    'bridges2': {'url': BRIDGES2, 'allowed_prefix': BRIDGES2},
    'aces': {'url': ACES, 'allowed_prefix': ACES},
    'anvil': {'url': ANVIL, 'allowed_prefix': ANVIL},
    'cloudbank': {'url': CLOUDBANK, 'allowed_prefix': CLOUDBANK},
    'delta': {'url': DELTA, 'allowed_prefix': DELTA},
    'deltaai': {'url': DELTAAI, 'allowed_prefix': DELTAAI},
    'derecho': {'url': DERECHO, 'allowed_prefix': DERECHO},
    'expanse': {'url': EXPANSE, 'allowed_prefix': EXPANSE},
    'granite': {'url': GRANITE, 'allowed_prefix': GRANITE},
    'jetstream2': {'url': JETSTREAM2, 'allowed_prefix': JETSTREAM2},
    'kyric': {'url': KYRIC, 'allowed_prefix': KYRIC},
    'launch': {'url': LAUNCH, 'allowed_prefix': LAUNCH},
    'neocortex': {'url': NEOCORTEX, 'allowed_prefix': NEOCORTEX},
    'ookami': {'url': OOKAMI, 'allowed_prefix': OOKAMI},
    'osn': {'url': OSN, 'allowed_prefix': OSN},
    'osg': {'url': OSG, 'allowed_prefix': OSG},
    'pnrp': {'url': PNRP, 'allowed_prefix': PNRP},
    'ranch': {'url': RANCH, 'allowed_prefix': RANCH},
    'repacss': {'url': REPACSS, 'allowed_prefix': REPACSS},
    'sage': {'url': SAGE, 'allowed_prefix': SAGE},
    'stampede3': {'url': STAMPEDE3, 'allowed_prefix': STAMPEDE3},
    'voyager': {'url': VOYAGER, 'allowed_prefix': VOYAGER},
}

class Crawler:
    def __init__(self):
        self.visited_urls = []
        print("Which RP site would you like to crawl? Please enter the RP name (e.g., deltaai, sage, derecho) without spaces or special characters:")
        desiredRP = input("> ").strip().lower()
        if desiredRP not in RP_DEFS:
            raise ValueError(f"Unknown RP name: {desiredRP}. Please use one of: {', '.join(RP_DEFS.keys())}")
        self.csv_file = desiredRP + '.csv'
        self.allowed_prefix = RP_DEFS[desiredRP]['allowed_prefix']
        self.urls_to_visit = [RP_DEFS[desiredRP]['url']]
        # Clear the CSV file at the start
        with open(self.csv_file, 'w', encoding='utf-8') as f:
            f.write('url\n')

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if not path:
                continue
            # Convert relative URLs to absolute
            abs_url = urljoin(url, path)
            # Only yield URLs within the allowed prefix
            if abs_url.startswith(self.allowed_prefix):
                yield abs_url

    def add_url_to_visit(self, url):
        if (
            url and
            url.startswith(self.allowed_prefix) and
            url not in self.visited_urls and
            url not in self.urls_to_visit
        ):
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)
        # After crawling, write all unique visited URLs to the CSV
        with open(self.csv_file, 'a', encoding='utf-8') as f:
            for url in self.visited_urls:
                f.write(f'{url}\n')
        print(f"Crawling complete. All visited URLs have been saved to {self.csv_file}.")

if __name__ == '__main__':
    Crawler().run()