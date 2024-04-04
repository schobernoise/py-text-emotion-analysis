import sys
import requests
from bs4 import BeautifulSoup
import justext


def parse_blog_article(url):
    response = requests.get(url)
    main_text = ""

    paragraphs = justext.justext(response.content, justext.get_stoplist("German"))

    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            main_text += paragraph.text
            # print(paragraph.text)

    # Initialize the result dictionary
    result = {"heading": "Not found", "subheading": "Not found", "article": main_text}

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find and update the main heading
        main_heading = soup.find("h1")
        if main_heading:
            result["heading"] = main_heading.text

        # Find and update the subheading
        subheading = soup.find("h2")
        if subheading:
            result["subheading"] = subheading.text

        # Find and update the main content
        main_content = soup.find("div", class_="main-content")
        if main_content:
            result["article"] = main_text

    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        URL = sys.argv[1]
        article_data = parse_blog_article(URL)
        print(article_data)
    else:
        print("Please provide a URL as a command-line argument.")
