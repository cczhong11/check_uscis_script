import requests
import sys
import re
from bs4 import BeautifulSoup 

from multiprocessing import Pool
import argparse

def init_arg(parser):
    parser.add_argument('--start', type=int, default=1990200000, help='Start id')
    parser.add_argument('--range', type=int, default=100, help='Search range')
    parser.add_argument('--loc', type=str, default='YSC', help='Process location, default is YSC')
    parser.add_argument('--seq', action='store_true',help='Start with sequential version')
    parser.add_argument('-v', action='store_true',help='print all status')
    parser.add_argument('-verr', action='store_true',help='print all error message')
    opt = parser.parse_args()
    return vars(opt)

class USCIS(object):

    def __init__(self, parser):
        self.opt = init_arg(parser)
       
        
    def getstatus(self,num):
    
        r= requests.post('https://egov.uscis.gov/casestatus/mycasestatus.do',data={"changeLocale":"","appReceiptNum":num,   "initCaseSearch":"CHECK STATUS"})
        try:
            s=BeautifulSoup(r.content,"lxml")
            rs = s.find('div',"current-status-sec").text
            rs = rs.replace("Your Current Status:","")
            rs = re.sub(r'[\t\n\r+]',"",rs)
            if self.opt["v"]:
                print("{}:{}".format(num,rs.strip()))
            if "Received" in rs:
                return 1
            if "Produced" in rs or "Delivered" in rs or "Mailed To Me" in rs or "Picked" in rs:
                return -1
            
        except Exception as e:
            if self.opt["verr"]:
                print(e)
        return 0


    def multiprocess(self,nums):
        p = Pool(10) # if this value is too big, USCIS would block your ip
        rs = p.map(self.getstatus, nums) # run multi processor version
        p.terminate()
        p.join()
        print(f"Produced number is : {-sum(i for i in rs if i is not None and i < 0)}")
        print(f"Received number is : {sum(i for i in rs if i is not None and i > 0)}")
    
    def sequential(self,nums):
        rec = 0
        pro = 0
        for i in nums:
            rs = self.getstatus(i)
            if rs > 0:
                rec+=rs
            elif rs < 0:
                pro-=rs
        print(f"Produced number is : {pro}")
        print(f"Received number is : {rec}")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    client = USCIS(args)
    
    search_list = []
    for i in range(client.opt["range"]):
        search_item = f"{client.opt['loc']}{client.opt['start']+i}"
        search_list.append(search_item)
    print(f"Start num is {client.opt['loc']}{client.opt['start']}")
    print(f"End num is {client.opt['loc']}{client.opt['start']+client.opt['range']-1}")
    if client.opt["seq"]:
        client.sequential(search_list)
    else:
        client.multiprocess(search_list)
