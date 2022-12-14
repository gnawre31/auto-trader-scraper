
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import datetime
import time


import psycopg2

# # connect to db
# conn = psycopg2.connect(
#     host="localhost",
#     database="dbname",
#     user="postgres",
#     password="postgres"
# )

# # cursor
# cur = conn.cursor()

# # execute
# cur.execute("SELECT * FROM table")
# rows = cur.fetchall()


s = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=s)


def initialize_browser():
    driver.get("https://www.autotrader.ca/cars/?rcp=15&rcs=0&srt=35&prx=-1&loc=M2N7H7&hprc=True&wcp=True&sts=Used&inMarket=advancedSearch")
    # driver.get("https://www.autotrader.ca/cars/?rcp=15&rcs=0&srt=10&prx=-1&loc=M2N7H7&hprc=True&wcp=True&sts=Used&adtype=Private&inMarket=advancedSearch")

    # cookie banner may block first link. Close cookie banner if it is there
    if driver.find_element(By.XPATH, "//div[@id='cookie-banner']"):
        driver.find_element(
            By.XPATH, "//button[@class='close-button']").click()

    # click first result
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-list-numerical-position='1']"))).click()

    counter = 0

    while(True):
        # 2 second delay to give browser time to load
        counter += 1
        time.sleep(2)

        # data
        data = []

        # parser
        sp = BeautifulSoup(driver.page_source, 'html.parser')

        # extract vehicle and location data from page URL
        # link = sp.find("link", {"rel": "canonical"})['href']
        link = sp.find("link", {"rel": "canonical"})
        if link != None:
            link = link['href']
            splitLink = link.split('/')
            try:
                brand = splitLink[4]
                model = splitLink[5]
                city = splitLink[6]
                province = splitLink[7]
            except:
                brand = model = city = province = None
                pass
        else:
            brand = model = city = province = None
        data.append({"brand": brand})
        data.append({"model": model})
        data.append({"city": city})
        data.append({"province": province})

        # extract listing id
        # id = sp.findAll("div", {"id": "vdpContainer"})['data-fdmid']
        id = sp.find("div", {"id": "vdpContainer"})
        if id != None:
            id = id['data-fdmid']
        data.append({"id": id})

        # extract post details
        postingTitle = sp.find("title")
        if postingTitle != None:
            postingTitle = postingTitle.text
        data.append({"postingTitle": postingTitle})

        price = sp.find("p", {"class": "hero-price"})
        if price != None:
            price = price.text
        data.append({"price": price})

        mileage = sp.find("p", {"id": "vdp-hl-mileage"})
        if mileage != None:
            mileage = mileage.text
        data.append({"mileage": mileage})

        transmission = sp.find("p", {"id": "vdp-hl-transmission"})
        if transmission != None:
            transmission = transmission.text
        data.append({"transmission": transmission})

        drivetrain = sp.find("p", {"id": "vdp-hl-drivetrain"})
        if drivetrain != None:
            drivetrain = drivetrain.text
        data.append({"drivetrain": drivetrain})

        # extract vehicle status and seller type
        # sellerType = sp.findAll("input", {"id": "sellerType"})['value']
        sellerType = sp.find("input", {"id": "sellerType"})
        if sellerType != None:
            sellerType = sellerType['value']
        data.append({"sellerType": sellerType})

        # vehicleStatus = sp.findAll("input", {"id": "vehicleStatus"})['value']
        vehicleStatus = sp.find("input", {"id": "vehicleStatus"})
        if vehicleStatus != None:
            vehicleStatus = vehicleStatus['value']
        data.append({"vehicleStatus": vehicleStatus})

        # vehicleType = sp.findAll("input", {"id": "vehicleType"})['value']
        vehicleType = sp.find("input", {"id": "vehicleType"})
        if vehicleType != None:
            vehicleType = vehicleType['value']
        data.append({"vehicleType": vehicleType})

        # is this page a priority listing?
        # non priority listing pages used to track if scraped before
        # do this after current site has been scraped in entirety
        postTypeText = sp.find("p", {"id": "navigationTitle"})
        if postTypeText != None:
            postTypeText = postTypeText.text
            isNotPriorityListing = "Priority Listing" in postTypeText
        data.append({"postTypeText": postTypeText})

        # extract posted date from photo url
        # photoURL = sp.findAll("img", {"id": "mainPhoto"})['src']
        photoURL = sp.find("img", {"id": "mainPhoto"})
        if photoURL != None:
            photoURL = photoURL['src']
            splitPhotoURL = photoURL.split("/")
            try:
                if(sellerType == 'Dealer'):
                    year = splitPhotoURL[5][:4]
                    month = splitPhotoURL[5][4:]
                    day = splitPhotoURL[6][:2]
                else:
                    year = splitPhotoURL[4]
                    month = splitPhotoURL[5]
                    day = splitPhotoURL[6]
                postedDate = datetime.date(int(year), int(month), int(day))
            except:
                postedDate = None
                pass
        else:
            postedDate = None
        data.append({"postedDate": postedDate})

        # print(id)
        # print('VEHICLE:', brand, model)
        # print('LOCATION:', city, province)

        # print(postingTitle.text)
        # print(price.text)
        # print(km)
        # print(sellerType)
        # print(splitPhotoURL)
        # print(postedDate)
        # print(isNotPriorityListing)
        print(data)
        print(counter)
        # print(isNotPriorityListing)

        # click next page
        try:
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@id='nextMobileAdLink']"))).click()

        except:
            print("NEXT BUTTON NOT FOUND")
            driver.quit()
            break
        # break


# run browser init
initialize_browser()
# conn.close()
