import sys
import time
import pandas as pd
import spacy
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from comments.analyse import preprocess_text, write_frequent_terms


def get_community_page_comments():
    comments = []
    cs = driver.find_elements_by_xpath('//*[@id="main"]')
    for c in cs:
        try:
            comment = c.find_element_by_id("content-text")
            comments.append(comment.text)
        except:
            pass
    return comments


def scroll_driver(scroll_pause_time, max_scrolls):
    num_scrolls = 0
    while num_scrolls < max_scrolls:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, 30000);")

        # Wait to load page
        time.sleep(scroll_pause_time)
        num_scrolls += 1
        print("Scrolling... {}/{}".format(num_scrolls, max_scrolls))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception(
            "Not enough arguments, pass the community poll URL after the command."
        )
    
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)


    url = sys.argv[1]
    driver.get(url)

    # click privacy agreement button
    print("Scrolling page...")
    button = driver.find_element_by_xpath('//button[normalize-space()="I agree"]')
    button.click()
    time.sleep(3)

    # scroll down page
    scroll_driver(scroll_pause_time=0.1, max_scrolls=300)
    print("Scraping comments...")
    comments = get_community_page_comments()

    print("Calculating named entities...")
    entities = Counter()
    nlp = spacy.load("en_core_web_md")
    for c in comments:
        c = preprocess_text(c)
        text_entities = nlp(c)
        for x in text_entities.ents:
            x_processed = x.text.lower()
            entities[x_processed] += 1
    driver.quit()
    
    print("Saving .csv files...")
    df = pd.DataFrame(comments, columns=["comment"])
    df.to_csv("community_poll_comments.csv", index=False)
    write_frequent_terms(entities, "community_poll_terms.csv")

    print(f"Scraped {len(comments)} comments")