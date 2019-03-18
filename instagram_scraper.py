import time
from lxml import html
from selenium import webdriver
from collections import defaultdict
import json


def handle_row(row, data, a_tags):
    """
    iterates through each post in the row
    :param row: object of the specific row
    :param data: dict format of the final data
    :param a_tags: array of strings containing href's
    :return: None
    """
    single_post = defaultdict()

    try:
        for post in row:

            # Checks if the post card is empty or not
            if "class" in post.attrib:
                single_post["post_link"] = post[0].attrib["href"]

                # Extract post info
                if single_post["post_link"] not in a_tags:
                    single_post["alt"] = post[0][0][0][0].attrib["alt"] if "alt" in post[0][0][0][0].attrib else ""
                    single_post["img_src"] = post[0][0][0][0].attrib["src"] if "src" in post[0][0][0][0].attrib else ""
                    data["posts"].append(single_post)
                    a_tags.append(single_post["post_link"])
                    single_post = defaultdict()
                else:
                    break
    except Exception as e:
        print("Error while handling individual post")


def handle_post_body(row, data, a_tags):
    """
    iterates through each row in the posts
    :param row: object of the specific row
    :param data: dict format of the final data
    :param a_tags: array of strings containing href's
    :return: None
    """
    try:
        if row.attrib["class"] == "Nnq7C weEfm":
            handle_row(row, data, a_tags)
    except Exception as e:
        print("Error while handling row")


def main():
    """
    main function
    :return: None
    """
    try:
        # SetUp Firefox driver
        options = webdriver.FirefoxOptions()
        options.headless = True
        options.Proxy = None
        fp = webdriver.FirefoxProfile()
        fp.set_preference("http.response.timeout", 400)
        fp.set_preference("dom.max_script_run_time", 240)
        driver = webdriver.Firefox(options=options, firefox_profile=fp)
    except Exception as e:
        print("Error while initializing driver")

    try:
        url = input()  # "https://www.instagram.com/vishnumanchu/"
        # Get page source
        driver.get(url)  # Enter the instagram page url
        page = driver.page_source.encode('utf-8')

        # Convert html page source to tree
        tree = html.fromstring(page)

        # Fetch header section data
        main_body = tree.find(".//header[@class=\'vtbgv \']")

        data = defaultdict()

        data["profile_picture_data"] = []
        profile_picture_data = defaultdict()
        profile_picture_data["profile_picture_src"] = main_body.find(".//img").attrib["src"] if "src" in main_body.find(
            ".//img").attrib else ""
        profile_picture_data["profile_picture_alt"] = main_body.find(".//img").attrib["alt"] if "alt" in main_body.find(
            ".//img").attrib else ""
        data["profile_picture_data"].append(profile_picture_data)

        data["profile_name"] = main_body[1].find(".//div[@class=\'nZSzR\']")[0].text

        data["posts_count"] = main_body[1][1][0].find(".//span").text
        data["followers_count"] = main_body[1][1][1].find(".//span").text
        data["following_count"] = main_body[1][1][2].find(".//span").text

        data["profile_description"] = defaultdict()
        description_data = []

        if len(main_body[1]) > 0:
            if len(main_body[1][2]) > 0:
                for tag in main_body[1][2]:
                    if tag.text:
                        if len(tag.text.strip()) > 0:
                            description_data.append(tag.text)

        data["profile_description"] = description_data
    except Exception as e:
        print("Error while handling header section")

    data["posts"] = [{"private_account": False}]

    a_tags = []

    try:
        # Fetch posts section data
        if tree.find(".//div[@class=\'v9tJq \']")[1].attrib["class"] != "Nd_Rl _2z6nI":
            posts_body = tree.find('.//div[@class=\' _2z6nI\']')

            for row in posts_body[0][0][0].iterchildren():
                handle_post_body(row, data, a_tags)

            while len(set(a_tags)) != int(data["posts_count"]):

                # Scroll to bottom of the page
                height = driver.find_element_by_tag_name("footer").rect.get('y')
                driver.execute_script("window.scrollTo(0, " + str(height) + ")")
                time.sleep(1)

                # Fetch page source and convert to tree structure
                page = driver.page_source.encode('utf-8')
                tree = html.fromstring(page)

                # Fetch posts body data
                posts_body = tree.find('.//div[@class=\' _2z6nI\']')

                for row in posts_body[0][0][0].iterchildren():
                    handle_post_body(row, data, a_tags)

        else:
            data["posts"]["Private Account"] = True
    except Exception as e:
        print("Error while handling posts body")

    # Close the driver
    driver.close()

    with open('result.json', 'w') as fp:
        json.dump(data, fp)


if __name__ == "__main__":
    main()
