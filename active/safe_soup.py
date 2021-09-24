def safe_soup( target_url):
    import requests
    from bs4 import BeautifulSoup

    response = requests.get( target_url)
    if response.status_code == requests.codes.ok:
        return BeautifulSoup( response.text, 'html.parser')
