import json

class User:
    # _example_user = {
    #     "tg_user": "@i_tsupko",
    #     "oauth_access_token": "usRZdOxSYaEeKVW7LXVGa5nedUUoEL7CrJ2oOPsm",
    #     "oauth_request_url": "http://8.18.31.21/oauth/authorize"
    #     "tg_chat_id": "24442585",
    #     "authorized": True,
    #     "pocket": "MyPocket"
    # }
    _filename = "data.json"

    users = []
    
    def _find(self, telegram_user):
        if len(self.users)>0:
            for i in range(len(self.users)):
                if self.users[i]["tg_user"] == telegram_user:
                    return i
        return -1

    def __init__(self):
        content_file = open(self._filename, 'r')
        content = content_file.read()
        content_file.close()
        self.users = json.loads(content)

    def _save(self):
        print(self.users)
        text_file = open(self._filename, "w")
        text_file.write(json.dumps(self.users))
        text_file.close()

    def getUsersIds(self):
        result = []
        for user in self.users:
            if user["authorized"]:
                result.append(user["tg_chat_id"])
        return result

    def hasMaster(self):
        return len(self.users) == 1

    def getMasterId(self):
        return self.users[0]["tg_chat_id"]

    def exists(self, username):
        return self._find(username)>-1

    def add(self,telegram_user,chat_id):
        self.users.append({
            "tg_user": telegram_user,
            "oauth_access_token" : "",
            "oauth_request_url": "",
            "tg_chat_id": chat_id,
            "authorized": False,
            "pocket": "",
            "pocket_account_id": 0,
            "pocket_currency": ""
        })
        self._save()
        return True

    def setPocket(self, telegram_user, value, account_id, account_currency):
        # TODO: check if self.telegram_user value
        self.users[self._find(telegram_user)]["pocket"] = value
        self.users[self._find(telegram_user)]["pocket_account_id"] = account_id
        self.users[self._find(telegram_user)]["pocket_currency"] = account_currency
        self._save()
        return True

    def setServer(self, telegram_user, value):
        # TODO: check if self.telegram_user exists
        self.users[self._find(telegram_user)]["oauth_request_url"] = value
        self._save()
        return True

    def setAccessToken(self, telegram_user, value):
        # TODO: check if self.telegram_user exists
        self.users[self._find(telegram_user)]["oauth_access_token"] = value
        self._save()
        return True

    def setAuthorized(self, telegram_user):
        # TODO: check if self.telegram_user exists
        self.users[self._find(telegram_user)]["authorized"] = True
        self._save()
        return True

    def getPocket(self,telegram_user):
        # TODO: check if self.telegram_user exists
        return self.users[self._find(telegram_user)]["pocket"]

    def getPocketAccountId(self,telegram_user):
        # TODO: check if self.telegram_user exists
        return self.users[self._find(telegram_user)]["pocket_account_id"]

    def getPocketCurrency(self,telegram_user):
        # TODO: check if self.telegram_user exists
        return self.users[self._find(telegram_user)]["pocket_currency"]

    def getUserAccessToken(self, telegram_user):
        # TODO: check if self.telegram_user exists
        return self.users[self._find(telegram_user)]["oauth_access_token"]

    def getAPIUrl(self, telegram_user):
        # TODO: check if self.telegram_user exists
        return self.users[self._find(telegram_user)]["oauth_request_url"]
