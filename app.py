from tkinter import *
from twilio.rest import Client
import requests

RATE_LIMIT = 0.5
BESTBUY_API_URL = 'https://www.bestbuy.ca/ecomm-api/availability/products?'


class AlertSystem:

    def __init__(self):
        pass
    def setUp(self):
        window = Tk()
        window.title("Best Buy Stock Alert App")
        window.geometry('1000x600')


        lbl = Label(window, text="Twilio account sid:")
        lbl.pack(fill=X)
        txt = Entry(window,width=50)
        txt.pack(expand=YES)
        txt.focus()

        lbl = Label(window, text="Twilio auth token:")
        lbl.pack(fill=X)
        txt = Entry(window,width=50)
        txt.pack(expand=YES)

        lbl = Label(window, text="Twilio messaging service sid:")
        lbl.pack(fill=X)
        txt = Entry(window,width=50)
        txt.pack(expand=YES)

        lbl = Label(window, text="Check every (?) seconds")
        lbl.pack(fill=X)
        spin = Spinbox(window, from_=5, to=1800, width=50)
        spin.pack(expand=YES)

        def set():
            self.index += 1
            listbox.insert(self.index,skuinput.get())
        def remove():
            self.index = 0
            listbox.Items.Clear();
        lbl = Label(window, text="Add link or sku to Watcher")
        lbl.pack(fill=X)
        skuinput = Entry(window,width=45)
        skuinput.pack(fill=X)
        button = Button(window, text = "add", command = set)
        button.pack(fill=X)
        button = Button(window, text = "remove all", command = remove)
        button.pack(fill=X)

        lbl = Label(window, text="Watch List:")
        lbl.pack(fill=X)
        listbox = Listbox(window)
        listbox.pack(fill=X)
        self.index = 0


        window.mainloop()

    def start(self):
        pass

class Watcher:
    def __init(self,links,messenger):
        self.skus = getSkus(links)
        self.messenger = messenger

    def checkStock(self):
        endpoint = BESTBUY_API_URL +'skus='
        first = True
        for sku,meta in self.skus.items():
            if first:
                endpoint +=sku
                first = False
            else:
                endpoint += '%'
                endpoint +=sku
        result = requests.get(endpoint)
        print(result.status_code)
        skusStatus = result.json().availabilities

        for skuStatus in skusStatus:
            pickupAvailble = skuStatus.pickup.purchasable
            shippingAvailable = skuStatus.shipping.purchasable
            self.skus[skuStatus.sku]['available'] = (pickupAvailble or shippingAvailable)
        print('Stock information updated ')

    def sendMessageIfAnyAvailable(self):
        message = ''
        newInStock = False
        for sku,meta in self.skus.items():
            if meta['available'] and not meta['messageSent']:
                message += "Item: " + sku + " is available at " +meta['link'] + '\n'
                self.skus[sku]['messageSent'] = True
                newInStock = True
        if newInStock:
            self.messenger.sendMessage(message)
            print('Message sent')

    def getSkus(self,links):
        dict = {}
        for link in links:
            sku = link.split("?")[0].split("/")[-1];
            if sku not in dict:
                dict[sku] = {}
                dict[sku]['link'] = link
                dict[sku]['messageSent'] = False
        return dict

class Messager:
    def __init__(self,account_sid,auth_token,sid,to):
        self.client = Client(account_sid, auth_token)
        self.sid = sid
        self.to = to

    def sendMessage(message):
        try:
            message = client.messages.create(
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
