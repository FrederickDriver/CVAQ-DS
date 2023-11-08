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
#python web.py --dp "C:/Program Files/Google/Chrome/Application/chrome.exe"
#                  --sw truck --s "D:/saved_img/pick_up_truck/"

delay = 2


def get_im(wd,delay,url):
    def scroll(driver):
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        time.sleep(delay)
    url = url
    wd.get(url)

    skips = 0
    get_end(wd)
    thumbnails = wd.find_elements(By.CLASS_NAME, 'Q4LuWd')
    
    image_urls = add_img(wd,thumbnails,skips)

    print(len(image_urls))
    return image_urls

def add_img(wd,thumbnails,skips):
    image_urls = set()
    for img in thumbnails:
        try:
            img.click()
            time.sleep(delay)
        except:
            continue
        images = wd.find_elements(By.XPATH, "//img[@jsname='kn3ccd']")
        #print(images)
        for image in images:
            if image.get_attribute('src') in image_urls:
                #print("in break")
                break
            if image.get_attribute('src') and \
                    'http' in image.get_attribute('src'):
                image_urls.add(image.get_attribute('src'))
                #print("add")
    return image_urls
    

def get_end(wd):
    scroll(wd)
    scroll(wd)
    scroll(wd)
    scroll(wd)
    scroll(wd)
    WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                            "input[value='Show more results']"))).click()
    scroll(wd)
    scroll(wd)
    scroll(wd)
    scroll(wd)  

def scroll(driver):
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
    time.sleep(delay)

def download_image(path, url, file_name, image_type='PNG',verbose=True):
    try:
        time = dt.now()
        cur_time = time.strftime('%H:%M:%S')
        image_content = requests.get(url,timeout=8).content
        #print(url)
        #img_file = io.BytesIO(image_content)
        #image = Image.open(img_file)
        file_pth = path + file_name

        with open(file_pth, 'wb') as file:
            file.write(image_content)

        if verbose == True:
            print(f'The image: {file_pth} downloaded successful at {cur_time}')
    except Exception as e:
        print(f'download failed due to:\n: {str(e)}')

def google_search(wd,searchterm):
    page = "http://www.google.com/"
    landing = wd.get(page)
    WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.NAME,
                                    "q"))).send_keys(searchterm+Keys.RETURN)
    
    WebDriverWait(wd, 20).until(EC.element_to_be_clickable((By.CLASS_NAME,
                                                "LatpMc"))).click()
    #imagesLink = wd.find_elements(By.CLASS_NAME ,"LatpMc nPDzT T3FoJb")
    #print(imagesLink)
    #WebDriverWait(wd, 10)
    #WebDriverWait(wd, 2)
    #imagesLink.click()
    #WebDriverWait(sendsearch, '10')
    #logo = driver.find_element_by_xpath('//*[@id="rg_s"]/div[1]/a').click()
    #WebDriverWait(logo, '10')
    #logolink = driver.find_element_by_xpath('//*[@id="irc_cc"]/div[3]/div[1]/div[2]/div[2]/a')
    #WebDriverWait(logolink, '10')
    #actions.move_to_element(logolink).click(logolink)  

    #print(wd.current_url)
    return wd.current_url


parser = argparse.ArgumentParser()
parser.add_argument("--dp",
                    help="This is thepath to you Chrome driver, driver path")
parser.add_argument("--sw",
                    help="This is the word that you want to search on Chrome, search words")
parser.add_argument("--s",
                    help="This is path of where you want to put the image")
args = parser.parse_args()

DRIVER_PATH = args.dp
options = Options()
options.headless = True
options.page_load_strategy = 'normal'
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

urls_image = google_search(driver,args.sw)

#'D:/saved_img/pick_up_truck'

save_path = args.s

if not os.path.exists(save_path):
    print(f'Make directory: {str(save_path)}')
    os.makedirs(save_path)
            
urls = get_im(driver,delay,urls_image)

for i,url in enumerate(urls):
    download_image(path=f'{save_path}',
                   url=url,file_name=str(i+1)+'.png',verbose=True)
        
driver.quit()
    
#get_im(driver,delay,max_lm,pickup_truck)
