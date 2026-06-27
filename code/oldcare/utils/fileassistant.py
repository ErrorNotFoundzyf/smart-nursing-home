# -*- coding: utf-8 -*-
'''
文件处理相关的函数
'''

import numpy as np
import pandas as pd
import json
import requests
import csv

def get_people_info(people_info_path):
    dataset = pd.read_csv(people_info_path)

    # 得到ID->姓名的map
    id_card_to_name = {}
    id_card_to_type = {}
    
    for index, row in dataset.iterrows():
        id_card_to_name[row[0]] = row[1]
        id_card_to_type[row[0]] = row[2]
        
    return id_card_to_name, id_card_to_type
                
def get_facial_expression_info(facial_expression_info_path):
    dataset = pd.read_csv(facial_expression_info_path)

    # 得到摄像头ID->摄像头名字的map
    facial_expression_id_to_name = {}

    for index, row in dataset.iterrows():
        facial_expression_id_to_name[row[0]] = row[1]
        
    return facial_expression_id_to_name

def generate_people_info(people_info_path):
    # old people
    res = requests.get('http://127.0.0.1:5000/oldpeoplemanagement/api/getinfolist')
    old_people_info_content = res.content.decode('utf-8')
    old_people_info_json = json.loads(old_people_info_content)
    old_people_info_list = old_people_info_json['json_list']
    
    # employee
    res = requests.get('http://127.0.0.1:5000/employeemanagement/api/getinfolist')
    employee_info_content = res.content.decode('utf-8')
    employee_info_json = json.loads(employee_info_content)
    employee_info_list = employee_info_json['json_list']
    
    # volunteer
    res = requests.get('http://127.0.0.1:5000/volunteermanagement/api/getinfolist')
    volunteer_info_content = res.content.decode('utf-8')
    volunteer_info_json = json.loads(volunteer_info_content)
    volunteer_info_list = volunteer_info_json['json_list']
    
    # generate data
    csv_write = csv.writer(open(people_info_path,'w'), dialect='excel')
    csv_write.writerow(['id_card', 'name', 'type']) # head
    csv_write.writerow(['Unknown', '陌生人', '']) # add stranger

    for i in old_people_info_list:
        csv_write.writerow([i['id'], i['name'], 'old_people'])
    for i in employee_info_list:
        csv_write.writerow([i['id'], i['name'], 'employee'])
    for i in volunteer_info_list:
        csv_write.writerow([i['id'], i['name'], 'volunteer'])
    