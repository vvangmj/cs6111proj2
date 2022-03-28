from googleapiclient.discovery import build
engine_id = "becd76ddad3b6ac04"
API_KEY = "AIzaSyCVc0q0-3jtaEc__0I8GORSt2339A4mRsw"
query = "bill gates microsoft"

def search(engine_id, API_KEY, query, url_set):
    service = build("customsearch", "v1",developerKey=API_KEY)
    res = service.cse().list(q=query, cx=engine_id,).execute()

    url_list = []

    for item in res['items']:
        # In case of KeyError
        url = ""
        if 'link' in item.keys():
            url = item['link']
        # In case of Repeated url
        if url not in url_set:
            url_list.append(url)
            url_set.add(url)

    return url_list

if __name__ == '__main__':
    url_set = set()
    url_list = search(engine_id, API_KEY, query, url_set)
    print(url_list)