import lxml.etree as ET
import pandas as pd
import re
import time

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
print(result)


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

tree = ET.parse('sample.html')
root = tree.getroot()
xshb_td = root.xpath('//td[@id="xshb_status"]')
xgl_td = root.xpath('//td[@id="xgl_status"]')
wmh_td = root.xpath('//td[@id="wmh_status"]')

ap_table = {'location': ['客厅', '卧室', '书房'], 'mac': ['14:DE:39:F4:AF:FE', 'A0:DE:0F:91:E3:7A', 'A0:DE:0F:91:CB:D9']}
ap_df = pd.DataFrame(ap_table)

if xshb_status == 'out':
    xshb_td[0].text = '不在家'
else:
    location = ap_df.loc[ap_df['mac'] == xshb, 'location'].iloc[0]
    xshb_td[0].text = location

if xgl_status == 'out':
    xgl_td[0].text = '不在家'
else:
    location = ap_df.loc[ap_df['mac'] == xgl, 'location'].iloc[0]
    xgl_td[0].text = location

if wmh_status == 'out':
    wmh_td[0].text = '不在家'
else:
    location = ap_df.loc[ap_df['mac'] == wmh, 'location'].iloc[0]
    wmh_td[0].text = location

localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
refresh_time = root.xpath('//p[@id="refresh_time"]')
refresh_time[0].text = str(localtime)

tree.write('sample.html', pretty_print=True)
