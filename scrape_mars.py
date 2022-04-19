# put all the data called from jupyternotebook
# put into a dictionary for all the results

from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd 
import datetime as dt 
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver
    #browser = Browser("chrome", executable_path="chromedriver", headless=True)
    
    # Set executable path and initialize the chrome browser in splinter 
    executable_path= {'executable_path': ChromeDriverManager().install()}
    #executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    # Since these are pairs 
    news_title, news_paragraph= mars_news(browser)
    hemisphere_image_urls=hemisphere(browser)
    
    # Run all scraping functions and store results in dictionary 
    data={
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


## > SCRAPE MARS NEWS <

def mars_news(browser):

    # visit NASA website 
    url= 'https://redplanetscience.com/'
    browser.visit(url)

    #Optional delay for website 
    # Here we are searching for elements with a specific combination of tag (ul) and (li) and attriobute (item_lit) and (slide)
    # Ex. being <ul class= "item_list">
    browser.is_element_present_by_css("div.list_text", wait_time=1)

    # HTML Parser. Convert the brpwser html to a soup object and then quit the browser
    html= browser.html 
    news_soup= bs(html, 'html.parser')

    # Add try/except for error handling
    try:
        #slide_elem looks for <ul /> tags and descendents <li />
        # the period(.) is used for selecting classes such as item_list
        slide_elem= news_soup.select_one("div.list_text")

        # Chained the (.find) to slide_elem which says this variable holds lots of info, so look inside to find this specific entity
        # Get Title
        news_title=slide_elem.find('div', class_= 'content_title').get_text()
        # Get article body
        news_p= slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None,None

    return news_title, news_p


## > SCRAPE FEATURED IMAGES <

def featured_image(browser):

    # Visit URL 
    url= 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the full_image button
    
    # Find and click the full_image button
    full_img =  browser.find_by_tag('button')[1]
    full_img.click()
    html = browser.html
    img_soup = bs(html, 'html.parser')
    # Add try/except for error handling
    try:
        # Find the relative image url
        # The 'figure.lede' references the <figure /> tag and its class=lede
        # the 'a' is the next tag nested inside the <figure /> tag, as well as the 'img' tag
        # the .get('src') pulls the link to the image
        # WE are telling soup to go to figure tag, then within that look for an 'a' tag then within that look for a 'img' tag
        img_url_rel=img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
    # Need to get the FULL URL: Only had relative path before
    img_url= f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url
    

## > SCRAPE FACTS ABOUT MARS <

def mars_facts():
    
    # Add try/except for error handling
    try:
        # Creating DF by telling function to look for first html table in site it encounters by indexing it to zero
        df=pd.read_html('http://space-facts.com/mars/')[0]

    # BaseException, catches multiple types of errors
    except BaseException:
        return None
    
    # Assigning columns, and set 'description' as index 
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    #Convert back to HTML format, add bootstrap
    return df.to_html()

## > SCRAPE HEMISPHERE <

def hemisphere(browser):
    hemisphere_image_urls = []
    hemURL = 'https://marshemispheres.com/'
    browser.visit(hemURL)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')
    item = soup.find('div', class_ = 'collapsible results').find_all('div', class_ = 'item')
    for x in item:
        #image title
        imgTitle = x.find('h3').text
        #click on the link to get larger images size
        browser.click_link_by_partial_text(imgTitle)
        # HTML object
        html = browser.html
        # Parse HTML with Beautiful Soup
        soup = bs(html, 'html.parser')
        imgURL = soup.find('div', class_ = 'downloads').find('li').find('a')['href']
        dictionary = {"Title" : imgTitle, "img_url": hemURL + imgURL}
        hemisphere_image_urls.append(dictionary)
        #moving back on the browser https://splinter.readthedocs.io/en/latest/browser.html
        browser.back()
    return hemisphere_image_urls

if __name__== "__main__":
    # If running as script, print scrapped data
    print(scrape_all())