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
    url= 'https://mars.nasa.gov/news/'
    browser.visit(url)

    #Optional delay for website 
    # Here we are searching for elements with a specific combination of tag (ul) and (li) and attriobute (item_lit) and (slide)
    # Ex. being <ul class= "item_list">
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # HTML Parser. Convert the brpwser html to a soup object and then quit the browser
    html= browser.html 
    news_soup= bs(html, 'html.parser')

    # Add try/except for error handling
    try:
        #slide_elem looks for <ul /> tags and descendents <li />
        # the period(.) is used for selecting classes such as item_list
        slide_elem= news_soup.select_one('ul.item_list li.slide')

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
    url= 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mar'
    browser.visit(url)

    # Find and click the full_image button
    full_image_elem= browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that 
    # is_element_present_by_text() method to search for an element that has the provided text
    browser.is_element_present_by_text('more info', wait_time=1)

    # will take our string 'more info' and add link associated with it, then click
    more_info_elem=browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html=browser.html
    img_soup=bs(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url 
        # The 'figure.lede' references the <figure /> tag and its class=lede
        # the 'a' is the next tag nested inside the <figure /> tag, as well as the 'img' tag 
        # the .get('src') pulls the link to the image

        # WE are telling soup to go to figure tag, then within that look for an 'a' tag then within that look for a 'img' tag
        img_url_rel= img_soup.select_one('figure.lede a img').get("src")
    
    except AttributeError:
        return None
    # Need to get the FULL URL: Only had relative path before
    img_url= f'https://www.jpl.nasa.gov{img_url_rel}'

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

# def hemisphere(browser):
    
#     hemisphere_image_urls = []
#     hemURL = 'https://marshemispheres.com/'
#     browser.visit(hemURL)

#     html = browser.html
#     # Parse HTML with Beautiful Soup
#     soup = bs(html, 'html.parser')
#     item =bs.find('div', class_ = 'collapsible results').find('h2', class_ = 'item')


#     for x in item:
#         #image title
#         imgTitle = x.find('h3').text
#         #click on the link to get larger images size
#         browser.click_link_by_partial_text(imgTitle)
#         # HTML object
#         html = browser.html
#         # Parse HTML with Beautiful Soup
#         soup = bs(html, 'html.parser')

#         imgURL = bs.find('div', class_ = 'downloads').find('li').find('a')['href']

#         dictionary = {"Title" : imgTitle, "img_url": hemURL + imgURL}
#         hemisphere_image_urls.append(dictionary)
#         #moving back on the browser https://splinter.readthedocs.io/en/latest/browser.html
#         browser.back()
        
#     return hemisphere_image_urls

def scrap_hemisphere(html_text):
    
    hemURL = 'https://marshemispheres.com/'
    hemisphere_soup = bs(html_text, 'html.parser')
    
try:
        title_element = hemisphere_soup.find('h2', class_ = 'title').get_text()
        picture_element = hemisphere_soup.find('a', text='Sample').get('href')
        
except:
         "sorry, it doesn't work"
     
dictionary = {"Title" : imgTitle, "img_url": hemURL + imgURL}   
    

if __name__== "__main__":
    # If running as script, print scrapped data
    print(scrape_all())