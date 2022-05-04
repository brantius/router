from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import json
import time
from json2xml import json2xml
from json2xml.utils import readfromurl, readfromstring, readfromjson

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver_path = 'geckodriver.exe'
serv = Service(driver_path)
driver = webdriver.Firefox(service=serv, options=options)
url = 'http://192.168.3.1/html/index.html#/login'
driver.get(url)
driver.implicitly_wait(20)

#text = driver.find_element(by=By.ID, value='userpassword_ctrl')
text = driver.find_element(by=By.ID, value='userpassword_ctrl')
text.clear()
text.send_keys('bayer6986')

button = driver.find_element(by=By.ID, value='loginbtn')
button.click()

topology_url = 'http://192.168.3.1/api/device/topology'
topology = driver.get(topology_url)
driver.implicitly_wait(20)
#content = driver.page_source
topology_content = driver.find_element(by=By.XPATH, value='//div[@id="json"]').text

host_info_url = 'http://192.168.3.1/api/system/HostInfo'
host_info = driver.get(host_info_url)
driver.implicitly_wait(20)
host_info_content = driver.find_element(by=By.XPATH, value='//div[@id="json"]').text

driver.implicitly_wait(20)
driver.quit()

topology_data = readfromstring(topology_content)
topology_xml = json2xml.Json2xml(topology_data).to_xml()

host_info_data = readfromstring(host_info_content)
host_info_xml = json2xml.Json2xml(host_info_data).to_xml()

with open('topology.xml', 'w') as file:
    file.write(topology_xml)
    file.close()

with open('host_info.xml', 'w') as file:
    file.write(host_info_xml)
    file.close()
