from os.path import isfile
from urllib.parse import unquote
from translate import Translator
from time import sleep
class PostCloning:
    def __init__(self, api_session=None):
        self.__session = api_session
        self.__cloned_postid = None
        self.__cloned_postid_file = None
        self.__target_id = None
        print(f"({self.__session.login_mode}): Logged as {self.__session.name}")
    @staticmethod
    def __formatingPostId(idx):
        return f"/{idx.split('_')[0]}/post/{idx.split('_')[1]}"
    def open_target(self, target_id):
        self.__target_id = target_id
        self.__cloned_postid_file = f"./.data/{self.__target_id}_idpost_cloned.txt"
        if (isfile(self.__cloned_postid_file)): pass
        else: open(self.__cloned_postid_file, "a").close()
        self.__cloned_postid = [idx.replace("\n", "") for idx in list(open(self.__cloned_postid_file, "r").readlines())]
        return True
    def check_activity(self, limit):
        lastPost = self.__session.get_feed(self.__target_id, fromUser=True, limit=limit)
        newActivity = False
        for idx, post in enumerate(lastPost):
            if (self.__formatingPostId(post["id"]) not in self.__cloned_postid):
                newActivity = True
            else:
                newActivity = False
            yield idx, newActivity, post
    def __make_post_data(self, post, to_lang):
        translator= Translator(to_lang=to_lang)
        upimg = False
        upvideo = False
        postType = None
        data = {}
        pictureLink = ((post.get("picture","")).encode("utf8")).decode("utf-8")
        if ("message" in post):
            data["message"] = translator.translate(post["message"])
            postType = "Text"
        if ((post.get("link", "")).startswith("https://www.facebook.com")):
            if ("profil" in post.get("story", "")): # change photo profile
                #imgSource = seef.__session.get_imgsource_by_fbid(post)
                #postType = "Change Profile"
                #i can't change user's profile
                return False, False, False, False
            elif ("/videos/" in post["link"]) and (post["status_type"] == "added_video"):
                data["file_url"] = post["source"]
                data["description"] = data.pop("message")
                upvideo = True
                postType = "Videos"
            elif (post["status_type"] == "added_photos") and ("story" not in post): # just upload a photo
                data["url"] = self.__session.get_imgsource_by_fbid(post)
                upimg = True
                postType = "Photos"
            else: #Share someone's post
                data["link"] = post.get("link", "")
                postType = "Shared"
        elif ("url=http" in pictureLink): #Share link, like news, gif, other
            pre_link = unquote((pictureLink.split("&url=")[1]).split("&")[0])
            if (".gif" in pre_link):
                data["link"] = pre_link
                postType = "Gif"
            else:
                data["link"] = post["link"]
                postType = "Links"
        if (len(data)==0):
            #Post can't be parsed
            return False, False, False, False
        else:
            return postType, data, upimg, upvideo
    def clone_post(self, post, to_lang="id"):
        postType, data, upimg, upvideo = self.__make_post_data(post, to_lang=to_lang)
        if (data != False):
            publish = self.__session.publish(data=data, upimg=upimg, upvideo=upvideo)
            with open(self.__cloned_postid_file, "a") as f:
                f.write(f"{self.__formatingPostId(post['id'])}\n")
                f.close()
            return self.__formatingPostId(post['id']), self.__formatingPostId(publish['id']), postType
        else:
            return False, False, False