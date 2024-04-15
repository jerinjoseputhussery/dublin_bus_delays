import requests,zipfile

def download():
    url = 'https://www.transportforireland.ie/transitData/Data/GTFS_Realtime.zip'
    r = requests.get(url, allow_redirects=True)
    print('Latest GTFS file downloaded')
    open('GTFS_Realtime.zip', 'wb').write(r.content)

    with zipfile.ZipFile('GTFS_Realtime.zip', 'r') as zip_ref:
        zip_ref.extractall('GTFS_Realtime')
    print('GTFS files extraction completed')