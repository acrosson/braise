import gnp


def find_docs():
    f = gnp.get_google_news(gnp.EDITION_ENGLISH_US)
    stories = f['stories']
    urls = [story['link'] for story in stories]
    return urls


if __name__ == '__main__':
    find_docs()
