from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import io
from datetime import datetime as dt
from PIL import Image
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import argparse

#Sample Usage
#python web.py --sw truck --s "D:/saved_img/pick_up_truck/"

#The delay here is set to let the page load
delay = 2

#Main function that is used to get the image
def get_im(wd,delay,url):
    #Go to the page of the url
    url = url
    wd.get(url)
    #Perform a finited number of scroll to get to the end of the page
    get_end(wd)
    #Now find all small image
    thumbnails = wd.find_elements(By.CLASS_NAME, 'Q4LuWd')
    #Get the url for the image
    image_urls = add_img(wd,thumbnails)
    #Return the url
    
    return image_urls

#Function to obtain the url of images
def add_img(wd,thumbnails):
    #Initiate a set to check duplicate
    image_urls = set()
    #Iterate over the thumbnails
    for img in thumbnails:
        try:
            #Click the image to get the bigger image
            img.click()
            time.sleep(delay)
        except:
            continue
        #Find the bigger image with XPATH
        images = wd.find_elements(By.XPATH, "//img[@jsname='kn3ccd']")
        
        #Find the url of the image, if it is in the set then skip
        for image in images:
            if image.get_attribute('src') in image_urls:
                #print("in break")
                break
            if image.get_attribute('src') and \
                    'http' in image.get_attribute('src'):
                image_urls.add(image.get_attribute('src'))
                #print("add")
    return image_urls
    
#A scroll down function, Scroll 5 times to get to the button "show more result"
#Then click that button and scroll down 4 more times
#Usually it would include all pictures already
#Image after that would not be as relevant
#For a bad search, there might not be as many result to get the button
#Thus, it is in a try block
def get_end(wd):
    scroll(wd)
    scroll(wd)
    scroll(wd)
    scroll(wd)
    #scroll(wd)
    try:
        WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                            "input[value='Show more results']"))).click()
        scroll(wd)
        scroll(wd)
        scroll(wd)
        scroll(wd) 
    except:
        print("There is less than 4 pages of result")

#Scroll down script
def scroll(driver):
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
    time.sleep(delay)

#Image download
def download_image(path, url, file_name, image_type='PNG',verbose=True):
    try:
        time = dt.now()
        cur_time = time.strftime('%H:%M:%S')
        #Get the image content and timeout if request cannot be make
        image_content = requests.get(url,timeout=8).content
        #The path of the saved image
        file_pth = path + file_name

        #Save image
        with open(file_pth, 'wb') as file:
            file.write(image_content)

        #Print out the time when the image is saved
        if verbose == True:
            print(f'The image: {file_pth} downloaded successful at {cur_time}')

    #Print out the failed download
    except Exception as e:
        print(f'download failed due to:\n: {str(e)}')

#Search the google and return the url of the image page
def google_search(wd,searchterm):
    page = "http://www.google.com/"
    #Go to google.com
    landing = wd.get(page)
    #Wait for a bit and sendkeys to the query box and click return
    WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.NAME,
                                    "q"))).send_keys(searchterm+Keys.RETURN)
    #Wait for a bit and click the image tab to go to the image page
    WebDriverWait(wd, 20).until(EC.element_to_be_clickable((By.CLASS_NAME,
                                                "LatpMc"))).click()

    #Return the current url
    return wd.current_url

#Arg Parse, sw=search words, s=saved path
parser = argparse.ArgumentParser()
parser.add_argument("--sw",
    help="This is the word that you want to search on Chrome, search words")
parser.add_argument("--s",
    help="This is path of where you want to put the image. End with /")
args = parser.parse_args()


options = Options()
options.headless = True
options.page_load_strategy = 'normal'
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

urls_image = google_search(driver,args.sw)

#Save path
#Sample: 'D:/saved_img/pick_up_truck/'
#The last back slash is needed
save_path = args.s

#Create a directory if it does not exist
if not os.path.exists(save_path):
    print(f'Make directory: {str(save_path)}')
    os.makedirs(save_path)

#Run the get image function            
urls = get_im(driver,delay,urls_image)

#For everything in image urls, download
for i,url in enumerate(urls):
    download_image(path=f'{save_path}',
                   url=url,file_name=str(i+1)+'.png',verbose=True)
    
#Close driver
driver.quit()
    
#get_im(driver,delay,max_lm,pickup_truck)
