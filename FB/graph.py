from . import token
import json, requests, hashlib
from time import sleep
from sys import exit
class API():
    def __init__(self):
        self.__access_token = None
        self.__userdata = None
        self.login_mode = None
    def load_token(self):
        if (access_token := token.load()):
            self.__access_token = access_token
            self.__userdata = self.get_user_data("me")
            self.login_mode = "Loaded"
        else:
            return False
    def new(self, email, pw):
        if (access_token := token.generate(email, pw)):
            self.__access_token = access_token
            self.__userdata = self.get_user_data("me")
            self.login_mode = "New"
        else:
            return False
    def get_feed(self, target_id, fromUser=True, limit=1):
        if (limit<=0):
            print("Limit must be >= 1")
            limit = int(input("[?] set limit: "))
            if (limit <= 0):
                exit() #strhludh
        if (self.__access_token == None):
            print(f"Dismissed: missing access_token")
            exit()
        feed = json.loads(requests.get(f"https://graph.facebook.com/{target_id}?fields=feed&access_token={self.__access_token}", timeout=100).text)
        if ("error" in feed):
            print(feed["error"]["message"])
            exit()
        feed = feed["feed"]
        lastPost = []
        targetName = (self.get_user_data(target_id)).get("name", "")
        for post in feed["data"]:
            if (fromUser == True):
                if (post["from"]["name"] == targetName):
                    lastPost.append(post)
            else:
                lastPost.append(post)
            if (len(lastPost) >= limit):
                break
        if limit > 1:
            #Dibalik dari yg terlama biar gk berantakan urutan postnya
            return lastPost[::-1]
        else:
            return lastPost
    def get_user_data(self, id):
        if (self.__access_token == None):
            print(f"Dismissed: missing access_token")
            exit()
        data = json.loads(requests.get(f"https://graph.facebook.com/{id}?access_token={self.__access_token}", timeout=100).text)
        if ("name" in data):
            return data
        else:
            if (data.get("error", False)):
                print(f"ERROR ({data['error_code']}): {data['error']}")
                exit()
    def publish(self, data, upimg=False, upvideo=False):
        if (self.__access_token == None):
            print(f"Dismissed: missing access_token")
            exit()
        if (upimg): url = (f"https://graph.facebook.com/me/photos?access_token={self.__access_token}")
        elif (upvideo): url = (f"https://graph-video.facebook.com/v2.3/me/videos?access_token={self.__access_token}")
        else: url = (f"https://graph.facebook.com/me/feed?access_token={self.__access_token}")
        result = json.loads(requests.post(url, data=data, timeout=None).text)
        if (upvideo or upimg):
            #Menunggu untuk benar2 terupload
            sleep(50)
            return {"id": (self.get_feed("me", fromUser=True, limit=1))[0]["id"], "object_id": result.get("id", "")}
        else: return result
    def get_imgsource_by_fbid(self, post):
        fbid = (post["link"].split("fbid=")[1]).split("&")[0]
        imgSource = json.loads(requests.get(f"https://graph.facebook.com/{fbid}?access_token={self.__access_token}", timeout=100).text)
        return imgSource["images"][0]["source"]
    @property
    def token(self):
        return self.__access_token
    @property
    def email(self):
        return self.__userdata.get("email")
    @property
    def name(self):
        return self.__userdata.get("name")