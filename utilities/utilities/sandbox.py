from bs4 import BeautifulSoup

stats_table = None
try:
    html = '''
        <!doctype html>
        <html>
        <head>
        <title>Our Funky HTML Page</title>
        <meta name="description" content="Our first page">
        <meta name="keywords" content="html tutorial template">
        </head>
        <body>
        Content goes here.
        </body>
        </html>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    stats_tbody = soup.find('tbody')
    print(stats_tbody)
except Exception as e:
    print(e)

