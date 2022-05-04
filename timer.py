from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import json
import time
from json2xml import json2xml
from json2xml.utils import readfromurl, readfromstring, readfromjson
import lxml.etree as ET
import pandas as pd
import re
import time
import os

options = webdriver.FirefoxOptions()
#options.add_argument('--headless')
#options.add_argument('--disable-gpu')
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

driver.implicitly_wait(30)
button = driver.find_element(by=By.ID, value='loginbtn')
button.click()

topology_url = 'http://192.168.3.1/api/device/topology'
topology = driver.get(topology_url)
#wait = WebDriverWait(driver, 30, 0.5)
#element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="json"]')), message="")
driver.implicitly_wait(30)
#content = driver.page_source
topology_content = driver.find_element(by=By.XPATH, value='//div[@id="json"]').text
print('Topology Found!')

host_info_url = 'http://192.168.3.1/api/system/HostInfo'
host_info = driver.get(host_info_url)
driver.implicitly_wait(30)
host_info_content = driver.find_element(by=By.XPATH, value='//div[@id="json"]').text
print('Host Info Found!')
driver.implicitly_wait(30)
home_page = driver.get('http://192.168.3.1/html/index.html#/home')
driver.implicitly_wait(30)
logout_button = driver.find_element(by=By.ID, value='logout_btn')
logout_button.click()
driver.quit()

print('XML files have been downloaded successfully.')

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

tree = ET.parse('topology.xml')
router_count = int(tree.xpath('count(//all/item)'))

topology_df = pd.DataFrame(columns=['router', 'mac'])

count = 0
for i in range(1, 6):
    router_xpath = '//all/item[' + str(i) + ']/MACAddress/text()'
    devices_xpath = '//all/item[' + str(i) + ']//item/MACAddress/text()'
    router_mac = tree.xpath(router_xpath)
    devices_mac = tree.xpath(devices_xpath)
    for device in devices_mac:
        topology_df.loc[count] = [router_mac[0], device]
        count += 1

#print(topology_df)

file = open('host_info.xml').read()
mac = re.findall('<MACAddress type="str">(.+)</MACAddress>', file)
host_name = re.findall('<HostName type="str">(.+)</HostName>', file)
len_host = len(mac)
host_df = pd.DataFrame(columns=['host_name', 'mac'])

count = 0
while count != 88:
    host_df.loc[count] = [host_name[count], mac[count]]
    count += 1

result = pd.merge(topology_df, host_df, on='mac', how='left')
pd.set_option('display.max_rows', None)

print('XML files have been parsed successfully.')

try:
    fbz = result.loc[result['host_name'] == '小米MIX 2S', 'router'].iloc[0]
    #xgl = result.loc[result['host_name'] == 'HUAWEI Mate 30 5G', 'router'].iloc[0]
    #wmh = result.loc[result['host_name'] == 'HUAWEI_Mate_40E_Pro', 'router'].iloc[0]
except IndexError:
    fbz_status = 'out'
else:
    fbz_status = 'in'

try:
    xshb = result.loc[result['host_name'] == 'HUAWEI Mate 30 Pro 5G', 'router'].iloc[0]
    #xgl = result.loc[result['host_name'] == 'HUAWEI Mate 30 5G', 'router'].iloc[0]
    #wmh = result.loc[result['host_name'] == 'HUAWEI_Mate_40E_Pro', 'router'].iloc[0]
except IndexError:
    xshb_status = 'out'
else:
    xshb_status = 'in'


try:
    xgl = result.loc[result['host_name'] == 'HUAWEI Mate 30 5G', 'router'].iloc[0]
    #wmh = result.loc[result['host_name'] == 'HUAWEI_Mate_40E_Pro', 'router'].iloc[0]
except IndexError:
    xgl_status = 'out'
else:
    xgl_status = 'in'

try:
    wmh = result.loc[result['host_name'] == 'HUAWEI_Mate_40E_Pro', 'router'].iloc[0]
except IndexError:
    wmh_status = 'out'
else:
    wmh_status = 'in'

print('Location of residents has been successfully determined.')

tree = ET.parse('sample.html')
root = tree.getroot()
xshb_td = root.xpath('//td[@id="xshb_status"]')
xgl_td = root.xpath('//td[@id="xgl_status"]')
wmh_td = root.xpath('//td[@id="wmh_status"]')
fbz_td = root.xpath('//td[@id="fbz_status"]')

ap_table = {'location': ['客厅', '卧室', '书房'], 'mac': ['14:DE:39:F4:AF:FE', 'A0:DE:0F:91:E3:7A', 'A0:DE:0F:91:CB:D9']}
ap_df = pd.DataFrame(ap_table)

if xshb_status == 'out':
    xshb_td[0].text = '未找到'
else:
    location = ap_df.loc[ap_df['mac'] == xshb, 'location'].iloc[0]
    xshb_td[0].text = location

if xgl_status == 'out':
    xgl_td[0].text = '未找到'
else:
    location = ap_df.loc[ap_df['mac'] == xgl, 'location'].iloc[0]
    xgl_td[0].text = location

if wmh_status == 'out':
    wmh_td[0].text = '未找到'
else:
    location = ap_df.loc[ap_df['mac'] == wmh, 'location'].iloc[0]
    wmh_td[0].text = location

if fbz_status == 'out':
    fbz_td[0].text = '未找到'
else:
    location = ap_df.loc[ap_df['mac'] == fbz, 'location'].iloc[0]
    fbz_td[0].text = location

localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
refresh_time = root.xpath('//p[@id="refresh_time"]')
refresh_time[0].text = str(localtime)

tree.write('sample.html', pretty_print=True)

print('HTML file has been refreshed successfully.')
