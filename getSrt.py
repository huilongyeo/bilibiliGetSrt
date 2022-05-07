# A function to get bilibili cc subtitle 获取哔哩哔哩视频的cc字幕
# created by huilongyeo on 2022/5/6
import json
import math

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from msedge.selenium_tools import Edge, EdgeOptions
import time
import pickle
import os.path
import requests


# Connect Bilibili with login by selenium in Microsoft Edge
def getSrtJson(url):
    global driver  # driver 需要设为全局变量，否则会闪退
    options = EdgeOptions()  # use edge be driver
    options.use_chromium = True
    options.headless = False  # show edge driver
    # enable Performance Logging of Edge
    caps = DesiredCapabilities.EDGE
    caps['loggingPrefs'] = {'performance': 'ALL'}
    options.binary_location = r"C:\Program Files (x86)\Microsoft\EdgeCore\101.0.1210.32\msedge.exe"  # browser location
    options.add_argument("--ignore-certificate-errors")  # Ignores any certification errors if there is any
    options.add_experimental_option('w3c', False)  # run in non-W#C mode to get network log
    driver = Edge(options=options, executable_path=r"C:\Users\USER\Desktop\ACGN\bilibiliGetSrt\edgedriver_win64"
                                                   r"\msedgedriver.exe",
                  desired_capabilities=caps)  # edge driver location

    """
    发现bilibili登入需要验证，因此放弃使用web driver 登录
    # login Bilibili
    login = driver.find_element_by_class_name("header-login-entry")
    login.click()
    # wait ui show
    time.sleep(3)
    # bilibili登录的Xpath定位浮动，但发现是最后第二个，因此使用last()-1定位
    # send account
    driver.find_element_by_xpath("/html/body/div[last()-1]/div/div[2]/div[3]/div[2]/div[1]/input").send_keys(account)
    # send password
    driver.find_element_by_xpath("/html/body/div[last()-1]/div/div[2]/div[3]/div[2]/div[2]/div[1]/input").send_keys(password)
    driver.find_element_by_xpath("/html/body/div[last()-1]/div/div[2]/div[3]/div[2]/div[2]/div[1]/input").send_keys(Keys.ENTER)
    """

    # if have not cookie of login, let user login manual and save cookie
    if not os.path.exists('cookies.pickle'):
        web_url = "https://www.bilibili.com/"
        driver.get(web_url)

        # wait element response
        time.sleep(3)
        input("After login, press enter to continue...")
        with open("cookies.pickle", 'wb') as file:
            # 3rd argument 0 means ASCII protocol, avoid pickle garbled
            pickle.dump(driver.get_cookies(), file, 0)
        print(driver.get_cookies())
        driver.close()

    title = "null"  # save title of video
    # use cookies to login
    with open("cookies.pickle", 'rb') as file:
        cookiesList = pickle.load(file)
    # access before add cookie avoid driver request an empty page
    try:
        driver.get(url)
        for cookie in cookiesList:
            driver.add_cookie(cookie)

        # access again after driver get cookies
        driver.get(url)
        time.sleep(3)  # wait cc file response
        # get video title
        try:
            title = driver.find_element_by_xpath("//*[@id=\"app\"]/div[1]/div[4]/h1").get_attribute('textContent')
        except Exception:
            print("title can't found")

        logs = driver.get_log("performance")  # get performance log
        cc_url = None  # Store cc subtitle url
        for log in logs:
            network_log = json.loads(log["message"])["message"]
            # check if the key has network related value
            if ("Network.response" in network_log["method"]
                    or "Network.request" in network_log["method"]
                    or "Network.webSocket" in network_log["method"]):
                file = json.dumps(network_log)
                log_temp = json.loads(file)
                try:
                    url_temp = log_temp["params"]["request"]["url"]
                    if url_temp[len(url_temp) - 5:] == ".json":  # find josn file
                        cc_url = url_temp
                except Exception:
                    pass

        driver.close()

    except Exception:
        print("invalid url")

    if cc_url:
        subtitle = requests.get(cc_url)
        return subtitle.json(), title

    else:
        print("find not subtitle")
        return "none", "none"


def json_to_srt(srtJson, title):
    file = ''
    i = 1  # sequence number
    for data in srtJson['body']:
        start = data['from']  # get start time
        stop = data['to']  # get stop time
        content = data['content']  # get the content of subtitle
        file += '{}\n'.format(i)  # add sequence number
        hour = math.floor(start) // 3600
        minute = (math.floor(start) - hour * 3600) // 60
        sec = math.floor(start) - hour * 3600 - minute * 60
        minisec = int(math.modf(start)[0] * 100)  # process start time
        file += str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(sec).zfill(2) + ',' + str(
            minisec).zfill(2)  # fill number by 0 and write to file
        file += ' --> '
        hour = math.floor(stop) // 3600
        minute = (math.floor(stop) - hour * 3600) // 60
        sec = math.floor(stop) - hour * 3600 - minute * 60
        minisec = abs(int(math.modf(stop)[0] * 100 - 1))  # -1 to avoid 2 subtitle show in same time
        file += str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(sec).zfill(2) + ',' + str(
            minisec).zfill(2)
        file += '\n' + content + '\n\n'  # write content to file
        i += 1

    try:
        with open("{}.srt".format(title), 'w', encoding='utf-8') as f:
            f.write(file)
            f.close()
            print("{}.srt".format(title))
    except Exception:
        with open("{}.srt".format("temp"), 'w', encoding='utf-8') as f:
            f.write(file)
            f.close()
            print("title error")
            print("{}.srt".format(title))
