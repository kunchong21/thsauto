
import requests
import time


def full_Code(stockCode):
    pre = str(stockCode[0:2])
    dict = {  "60":"sh", "68":"sh", "30":"sz", "00":"sz", "11":"sh", "12":"sz"}
    return dict[pre] + stockCode



def getReal(stockCode):
    fullCode = full_Code(stockCode)
    start = round(time.time() * 1000)
    url = 'https://qt.gtimg.cn/q='+fullCode+'&_=' + str(start)
    req = requests.get(url, timeout=2)
    arr = req.text.replace("\"","").split("=")[1].split(",")
    return arr