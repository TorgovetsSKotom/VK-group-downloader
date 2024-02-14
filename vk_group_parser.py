import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import fake_useragent
from threading import Thread, Lock
from pathlib import Path
import argparse

from os.path import dirname
# script_path = dirname(__file__)
cur_dir = Path.cwd()
current_user = os.getlogin()
user = fake_useragent.UserAgent().random

arg_URL = 'https://vk.com/touhou_comics'    # url группы
num_cycle = 5                               # количество циклов загрузки страницы
image_list = None
end_flag = False

argparser = argparse.ArgumentParser(description="Download all images from post in VK group")
argparser.add_argument("--url", "-u", type=str, dest="URL", default=arg_URL, help="URL of the VK group")
argparser.add_argument("--output", "-o", type=str, dest="PATH", default=os.path.join(Path.home(), 'Downloads'), help="Path to save images")
argparser.add_argument("--num_cycle", "-n", type=int, dest="NUM", default=num_cycle, help="Number cycle load new posts")
argparser.add_argument("--log_dir", "-l", type=str, dest="LOG", default=os.path.join(Path.home(), 'Downloads', 'vk_log'), help="Path to save log")
args = argparser.parse_args()
path_name = args.URL.split('/')[-1]

args.PATH = os.path.join(cur_dir, args.PATH, path_name)
args.LOG = os.path.join(cur_dir, args.LOG)

if not os.path.exists(args.PATH): os.makedirs(args.PATH)
if not os.path.exists(args.LOG): os.makedirs(args.LOG)

# driverPATH = os.path.join(script_path, 'chromedriver.exe')
# driverBIN = os.path.join(script_path, 'chromedriver')
# if os.name == 'posix':
#     driverPATH = driverBIN

# s = Service(executable_path=driverPATH)
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Firefox(options=options) # service=s


class ThreadSafeList:
    def __init__(self):
        self.lock = Lock()
        self.data = []

    def append(self, item):
        with self.lock:
            self.data.append(item)

    def remove(self, item):
        with self.lock:
            self.data.pop(item)

    def __str__(self):
        with self.lock:
            return str(self.data)
        
    def size(self):
        with self.lock:
            return len(self.data)


image_list = ThreadSafeList()


def downloader():
    global end_flag
    flag = True
    while True:
        if flag == True:
            time.sleep(2)
            flag = False
        # print(image_list.size())
        if not end_flag:
            if image_list.size() > 0:
                with image_list.lock:
                    image_url = image_list.data[0]
                image_list.remove(0)
                img_data = requests.get(image_url, headers={'user-agent': user})
                image = img_data.content
                if len(image) > 1000 and img_data.status_code == 200:
                    image_name = image_url.split('/')[-1]
                    # print(image_name)
                    if not os.path.exists(args.PATH +'/'+ image_name):
                        with open(args.PATH +'/'+ image_name, 'wb') as handler: handler.write(image)
        else:
            break


def main():
    global end_flag
    try:
        time_st = time.time()
        exclude_list = ['s/v1/i', 'emoji', 'sticker', 'pp.userapi.com', 'psv4.userapi.com']  # s/v1/ig1/ s/v1/if1/ s/v1/ig2/ s/v1/if2/
        log_list = []
        log_name = args.URL.split('/')[-1]
        log_file = os.path.join(args.LOG, f'{log_name}_log.txt')
        if os.path.exists(log_file):
            with open(log_file, 'r') as log:
                for line in log:
                    line = line.rstrip()
                    log_list.append(line)
        with open(log_file, 'a') as log:
            driver.maximize_window()
            driver.get(args.URL)
            procs = []
            for i in range(15):
                proc = Thread(target=downloader, daemon=True)
                proc.start()
                procs.append(proc)
            num = 0
            while num < args.NUM:
                posts = driver.find_elements(By.CLASS_NAME, 'post_content')
                # n = 0
                for post in posts[10*num:]:
                    imgs = post.find_elements(By.TAG_NAME, 'img')[:10]
                    for img in imgs:
                        image_url = img.get_attribute('src').split('?')[0].replace('impf/', '').replace('impg/', '')
                        if image_url not in image_list.data and image_url not in log_list and all(exc not in image_url for exc in exclude_list) and 'sun' in image_url:  # 'sun' is suspect
                            # print(image_url)
                            image_list.append(image_url)
                            log.write(f'{image_url}\n')
                            # n+=1
                # print(n)
                driver.execute_script(f'wall.showMore(20)')
                print('more', num+1)
                time.sleep(1)
                num+=1
            end_flag = True
            for proc in procs:
                proc.join()
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
        print(f'Время загрузки {time.time() - time_st} секунд')


if __name__ == "__main__":
    main()