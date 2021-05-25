import json
from tkinter import *
from twilio.rest import Client
from fake_useragent import UserAgent
import requests
import time

ua = UserAgent()
HEADERS = {'User-Agent':str(ua.chrome)}
RATE_LIMIT = 0.5
BESTBUY_API_URL = 'https://www.bestbuy.ca/ecomm-api/availability/products?'
BESTBUY_ITEM_PREFIX = 'https://www.bestbuy.ca/en-ca/product/'
class AlertSystem:

    def __init__(self):
        self.to = ''
    def setUp(self):
        window = Tk()
        window.title("Best Buy Stock Alert App")
        window.geometry('800x300')


        def set():
            self.index += 1
            self.listbox.insert(self.index,self.skuinput.get().split("?")[0].split("/")[-1])
            self.skuinput.delete(0, END);
        def remove():
            self.index = 0
            self.listbox.delete(0,END);
        def stop():
            self.started = False

        t1 = Label(window,text="Twilio account sid          ").grid(row=1)
        t2 = Label(window,text="Twilio auth token:          ").grid(row=2)
        t3 = Label(window,text="Twilio messaging service sid").grid(row=3)
        t4 = Label(window,text= "Check every (?) seconds     ").grid(row=4)
        t5 = Label(window,text= "sku or product link         ").grid(row=5)
        t6 = Label(window, text="Watch List:                 ").grid(row=0,column=2)



        self.accountSid = Entry(window)
        self.authToken = Entry(window)
        self.messagingServiceSid = Entry(window)
        self.frequency = Spinbox(window, from_=5, to=1800)
        self.skuinput = Entry(window)
        button1 = Button(window, text = "add to ->", command = set)
        button2 = Button(window, text = "remove all", command = remove)
        button3 = Button(window, text = "start", command = self.start)
        button4 = Button(window, text = "stop", command = stop)
        self.listbox = Listbox(window)
        self.index = 0

        self.accountSid.grid(row=1, column=1)
        self.authToken.grid(row=2, column=1)
        self.messagingServiceSid.grid(row=3, column=1)
        self.frequency.grid(row=4, column=1)
        self.skuinput.grid(row=5, column=1)
        button1.grid(row=5, column=2)
        button2.grid(row=9, column=4)
        button3.grid(row=9, column = 3)
        button4.grid(row=9, column = 5 )
        self.listbox.grid(row=1, column=3, rowspan=7, columnspan = 4)


        window.mainloop()

    def start(self):
        self.started = True
        self.messenger = Messager(self.accountSid.get(),self.authToken.get(),self.messagingServiceSid.get(),self.to)
        print(self.listbox.get(0,self.index))
        self.watcher = Watcher(self.listbox.get(0,self.index),self.messenger)

        while self.started:
            self.watcher.checkStock()
            time.sleep(int(self.frequency.get()))
            self.watcher.sendMessageIfAnyAvailable()


class Watcher:
    def __init__(self,links,messenger):
        self.skus = self.getSkus(links)
        self.messenger = messenger

    def checkStock(self):
        endpoint = BESTBUY_API_URL +'skus='
        first = True
        for sku,meta in self.skus.items():
            if first:
                endpoint +=sku
                first = False
            else:
                endpoint += '|'
                endpoint +=sku
        print(endpoint)
        result = requests.get(endpoint,headers = HEADERS)

        skusStatus = json.loads(result.content.decode('utf-8-sig'))['availabilities']

        for skuStatus in skusStatus:
            pickupAvailble = skuStatus['pickup']['purchasable']
            shippingAvailable = skuStatus['shipping']['purchasable']
            self.skus[skuStatus['sku']]['available'] = (pickupAvailble or shippingAvailable)
        print(self.skus)
        print('Stock information updated ')

    def sendMessageIfAnyAvailable(self):
        message = ''
        newInStock = False
        availableList = []
        for sku,meta in self.skus.items():
            if meta['available'] and not meta['messageSent']:
                message += "Item: " + sku + " is available at " +meta['link'] + '\n'
                self.skus[sku]['messageSent'] = True
                availableList.append(sku)
                newInStock = True
        if newInStock:
            self.messenger.sendMessage(message)
            Tk().messagebox.showinfo(title='Message Sent', message=str(availableList)+' is/are available')
            print('Message sent')

    def getSkus(self,links):
        dict = {}
        for link in links:
            sku = link.split("?")[0].split("/")[-1];
            if sku not in dict:
                dict[sku] = {}
                dict[sku]['link'] = BESTBUY_ITEM_PREFIX + sku
                dict[sku]['messageSent'] = False
        return dict

class Messager:
    def __init__(self,account_sid,auth_token,sid,to):
        self.client = Client(account_sid, auth_token)
        self.sid = sid
        self.to = to

    def sendMessage(self,message):
        try:
            print(self.sid)
            print(self.to)
            print(self.client.account_sid)
            print(self.client.auth)
            message = self.client.messages.create(
                                  messaging_service_sid=self.sid,
                                  body=message,
                                  to=self.to
                              )
            print(message + ' Sent')
        except Exception as e:
            print(e)


if __name__ == "__main__":
    board = AlertSystem()
    board.setUp()
