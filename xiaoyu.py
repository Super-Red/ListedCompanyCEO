#-*-coding:utf-8-*-

# 我要吃外卖！

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import csv
from datetime import *

def writeDataToFile(data, file):
    with open("{}".format(file), "a", encoding="utf-8") as csvFile:
        writer = csv.writer(csvFile)
        for index, value in enumerate(data):
            writer.writerow(value)
            print("{} done!".format(index))
    print("All Done!")

def getBorn(url, name):
    # click into the name's url and get the born date of the person 
    r = requests.get(url)
    r.encoding = "gbk"
    bsObj = BeautifulSoup(r.text, "html.parser")
    rows = bsObj.findAll("div", {"align":"center"})
    for index, row in enumerate(rows):
        if row.text == name:
            return rows[index+2].text[:4]+"-"+rows[index+2].text[4:6]
    return ""

def getInformation(stockID):
    url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpManager/stockid/{id}.phtml".format(id=stockID)
    r = requests.get(url)
    r.encoding = "gbk"
    bsObj = BeautifulSoup(r.text, "html.parser")
    rows = bsObj.findAll("td", {"class":"ccl"})
    chairman = []
    ceo = []
    names = {}
    for index, row in enumerate(rows):
        if row.text == "董事长":
            print("董事长:", end="")
            name = rows[index-1].a.text
            if name not in names :
                cha_url = "http://vip.stock.finance.sina.com.cn" + rows[index-1].a["href"]
                cha_url = quote(cha_url, safe='/:?=&', encoding="gbk")
                born = getBorn(cha_url, name)
                names[name] = born
            else:
                born = names[name]
            chairman.append([stockID, name, born, rows[index+1].text, rows[index+2].text])
            print([stockID, name, born, rows[index+1].text, rows[index+2].text])
        if row.text == "总裁" or row.text == "总经理":
            print("CEO:", end="")
            name = rows[index-1].a.text
            if name not in names :
                cha_url = "http://vip.stock.finance.sina.com.cn" + rows[index-1].a["href"]
                cha_url = quote(cha_url, safe='/:?=&', encoding="gbk")
                born = getBorn(cha_url, name)
                names[name] = born
            else:
                born = names[name]
            ceo.append([stockID, name, born, rows[index+1].text, rows[index+2].text])
            print([stockID, name, born, rows[index+1].text, rows[index+2].text])
    writeDataToFile(chairman, "chairman.csv")
    if ceo != []:
        writeDataToFile(ceo, "ceo.csv")
    print("All-")

def main(endpoint):
    with open("id.csv", "r") as csvFile:
        stockList = list(csv.reader(csvFile))
    for i, value in enumerate(stockList):
        if i > endpoint:
            getInformation(value[0])
            print("{num}: {id} has Done!".format(num=i, id=value[0]))

def is2015(start, end):
    # whether 2015 is between start and end 
    if start == "2015" or end == "2015":
        return True
    elif start == "":
        return False
    elif end == "":
        if int(start)<2015:
            return True
        else:
            return False
    elif int(start)<2015 and int(end)>2015:
        return True
    else:
        return False

def findChairman2015():
    with open("chairman.csv", "r", encoding="utf-8") as csvFile:
        reader = csv.reader(csvFile)
        for i, value in enumerate(csvFile):
            data = value.split(",")
            data[4] = data[4].strip()
            if data[2].endswith("-"):
                data[2] = data[2][:-1]
            startYear = data[3].split("-")[0]
            endYear = data[4].split("-")[0]
            if is2015(startYear, endYear):
                with open("chairman_2015.csv", "a", encoding="utf-8") as csvFile2:
                    writer = csv.writer(csvFile2)
                    writer.writerow(data)

def dropUselessData():
    # drop datas if one of the years' datas is missing (== "")
    datas = []
    with open("ceo_clean.csv", "r", encoding="utf-8") as csvFile_chair:
        reader = csv.reader(csvFile_chair)
        for i, value in enumerate(reader):
            if value[2] != "":
                value[2] = value[2][:4]
                datas.append(value[:-1])
            print(i)
        print(len(datas))
    # write the new datas into new file
    writeDataToFile(datas, "ceo_version2.csv")

def getDate(*dateList):
    result = []
    for dateString in dateList:
        year, month, day = list(map(int, dateString.split("-")))
        result.append(date(year, month, day))
    return result

def interactiveWorktime():
    with open("ceo_version2.csv", "r", encoding="utf-8") as csvFile:
        ceoList = list(csv.reader(csvFile))
    with open("chairman_version2.csv", "r", encoding="utf-8") as csvFile:
        chairmanList = list(csv.reader(csvFile))
    data = []
    ceo_end = date(2016, 12, 31)
    for index, ceo in enumerate(ceoList):
        ceo_start = getDate(ceo[3])[0]
        coporatetime = {}
        chairmans = [i for i in chairmanList if i[0] == ceo[0]]
        for chairman in chairmans:
            # CEO is not chairman
            if chairman[2] != ceo[2]:
                chair_start, chair_end = getDate(chairman[3], chairman[4])
                if chair_end > ceo_start:
                    chair_time = (chair_end-chair_start).days
                    # 3 circumstance in this situation 
                    if ceo_start > chair_start:
                        ceo_time = min((ceo_end-ceo_start).days, (chair_end-ceo_start).days)
                    elif ceo_end > chair_end:
                        ceo_time = (chair_end-chair_start).days
                    else:
                        ceo_time = (ceo_end-chair_start).days
                    if chairman[1] not in coporatetime:
                        coporatetime[chairman[1]] = [chairman[2], ceo_time, chair_time]
                    else:
                        coporatetime[chairman[1]][1] += ceo_time
                        coporatetime[chairman[1]][2] += chair_time
        if coporatetime != {}:
            for name, time in coporatetime.items():
                singleRow = [ceo[0], ceo[1], ceo[2]] + [name, ] + time
                data.append(singleRow)
    writeDataToFile(data, "ceo_chairman.csv")

def animal(year):
    animal = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    return animal[(year-4)%12]

def oppose(year1, year2):
    oppose = {  0 : {3, 6, 7},
                1 : {3, 4, 6, 7, 10},
                2 : {5, 8},
                3 : {0, 1, 4, 6, 9},
                4 : {1, 3, 4, 10},
                5 : {2, 8, 11},
                6 : {0, 1, 3, 6},
                7 : {0, 1, 10},
                8 : {2, 5, 11},
                9 : {0, 3, 9, 10},
                10: {1, 4, 7, 9},
                11: {5, 8, 11}}
    if (year2-4)%12 in oppose[(year1-4)%12]:
        return 1
    else:
        return 0

def final():
    data = []
    with open("ceo_chairman.csv", "r", encoding="utf-8") as csvFile:
        ceochairmanList = list(csv.reader(csvFile)) 
    for index, value in enumerate(ceochairmanList):
        ceo_animal = animal(int(value[2]))
        chairman_animal = animal(int(value[4]))
        value.insert(3, ceo_animal)
        value.insert(6, chairman_animal)
        value.append(oppose(int(value[2]), int(value[5])))
        value.append(int(value[7])/int(value[8]))
        data.append(value)
    writeDataToFile(data, "ceo_chairman_final.csv")
    