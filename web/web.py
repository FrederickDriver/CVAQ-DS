from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import io
from datetime import datetime as dt
from PIL import Image
import time
import os
from selenium.webdriver.common.by import By

DRIVER_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
options = Options()
options.headless = True
options.page_load_strategy = 'normal'
options.add_argument("--window-size=1920,1200")


pickup_truck = "https://www.google.com/search?q=pickup_truck&tbm=isch&ved=2ahUKEwiKyYfw5qiCAxUdMGIAHe73D7EQ2-cCegQIABAA&oq=pickup_truck&gs_lcp=CgNpbWcQAzIGCAAQBxAeMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMgQIABAeMgQIABAeMgQIABAeOgoIABCKBRCxAxBDOgUIABCABDoICAAQgAQQsQM6CAgAEAgQBxAeUKUGWI0jYLwyaAJwAHgAgAGyAYgB0giSAQM1LjWYAQCgAQGqAQtnd3Mtd2l6LWltZ8ABAQ&sclient=img&ei=FmpFZYrmDp3giLMP7u-_iAs&bih=704&biw=1463&rlz=1C1ONGR_enUS982US982"
delay = 5
max_lm = 5


driver = webdriver.Chrome(options=options)
#driver.get(pickup_truck)
#driver.quit()

def get_im(wd,delay,max_im,url):
    def scroll(driver):
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        time.sleep(delay)
    url = url
    wd.get(url)

    image_urls = set()
    skips = 0

    while len(image_urls) + skips < max_im:
        scroll(wd)
        thumbnails = wd.find_elements(By.CLASS_NAME, 'Q4LuWd')

        for img in thumbnails[len(image_urls) + skips:max_im]:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue

            images = wd.find_elements(By.XPATH, "//img[@jsname='kn3ccd']")
            #print(images)
            for image in images:
                if image.get_attribute('src') in image_urls:
                    max_lm += 1
                    skips += 1
                    #print("in break")
                    break
                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    #print("add")

    #print(image_urls)
    return image_urls

def download_image(path, url, file_name, image_type='PNG',verbose=True):
    try:
        time = dt.now()
        cur_time = time.strftime('%H:%M:%S')
        image_content = requests.get(url).content
        img_file = io.BytesIO(image_content)
        image = Image.open(img_file)
        file_pth = path + file_name

        with open(file_pth, 'wb') as file:
            image.save(file,image_type)

        if verbose == True:
            print(f'The image: {file_pth} downloaded successfully at {cur_time}')
    except Exception as e:
        print(f'download failed due to:\n: {str(e)}')

if __name__ == '__main__':
    google_url = [pickup_truck]

    labels = ['pickup_truck']

    assert(len(google_url)==len(labels))

    save_path = 'D:/saved_img/'
    for lb in labels:
        if not os.path.exists(save_path + lb):
            print(f'Make directory: {str(lb)}')
            os.makedirs(save_path+lb)
            
    for url_cur, lb in zip(google_url,labels):
        urls = get_im(driver,delay,max_lm,url_cur)

        for i,url in enumerate(urls):
            download_image(path=f'D:/saved_img/{lb}/',url=url,file_name=str(i+1)+'.png',verbose=True)
        
    driver.quit()
    
#get_im(driver,delay,max_lm,pickup_truck)
