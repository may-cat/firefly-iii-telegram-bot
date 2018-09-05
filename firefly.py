import urllib.request
import requests
import json
import datetime

class Firefly:
    def getBalances(self, username, users):
        url = users.getAPIUrl(username)+'/api/v1/accounts?type=asset'
        hdr = { 'Authorization': "Bearer "+users.getUserAccessToken(username) }

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        assets = []
        for asset in data["data"]:
            assets.append(asset["attributes"]["name"])

        return assets

    def getBalancesExtended(self, username, users):
        url = users.getAPIUrl(username)+'/api/v1/accounts?type=asset'
        hdr = { 'Authorization': "Bearer "+users.getUserAccessToken(username) }

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        assets = []
        for asset in data["data"]:
            assets.append(asset)

        return assets

    def getIncomes(self, username, users):
        url = users.getAPIUrl(username)+'/api/v1/accounts?type=revenue'
        hdr = { 'Authorization': "Bearer "+users.getUserAccessToken(username) }

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        incomes = []
        for income in data["data"]:
            incomes.append(income["attributes"]["name"])

        return incomes

    def getCurrentBalance(self, username, users):
        url = users.getAPIUrl(username)+'/api/v1/accounts/'+users.getPocketAccountId(username)
        hdr = { 'Authorization': "Bearer "+users.getUserAccessToken(username) }

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        return int(data['data']['attributes']['current_balance'])

    def getBudgets(self, username, users):
        url = users.getAPIUrl(username)+'/api/v1/budgets'
        hdr = { 'Authorization': "Bearer "+users.getUserAccessToken(username) }

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        budgets = []
        for budget in data["data"]:
            budgets.append(budget["attributes"]["name"])

        return budgets

    def spend(self, username, users, message_number, message_budget, message_text):
        now = datetime.datetime.now()
        url = users.getAPIUrl(username)+'/api/v1/transactions'
        payload = {
            "type": "withdrawal",
            "description": message_text,
            "date": now.strftime("%Y-%m-%d"),
            "transactions[0][amount]": message_number,
            "transactions[0][currency_code]": users.getPocketCurrency(username),
            "transactions[0][source_name]": users.getPocket(username),
            "transactions[0][budget_name]": message_budget
        }
        # Adding empty header as parameters are being sent in payload
        headers = {
            "Authorization": "Bearer "+users.getUserAccessToken(username),
            "Accept": "application/json"
        }
        r = requests.post(url, data=payload, headers=headers)
        # TODO: make a better one validation. r can be empty and will not be parsed further
        data = json.loads(r.text)
        if data["data"]:
            return True
        return False

    def take(self, username, users, message_number, message_balance, message_text):
        now = datetime.datetime.now()
        url = users.getAPIUrl(username)+'/api/v1/transactions'
        payload = {
            "type": "transfer",
            "description": message_text,
            "date": now.strftime("%Y-%m-%d"),
            "transactions[0][amount]": message_number,
            "transactions[0][currency_code]": users.getPocketCurrency(username),
            "transactions[0][source_name]": message_balance,
            "transactions[0][destination_name]": users.getPocket(username),
        }
        # Adding empty header as parameters are being sent in payload
        headers = {
            "Authorization": "Bearer "+users.getUserAccessToken(username),
            "Accept": "application/json"
        }
        r = requests.post(url, data=payload, headers=headers)
        # TODO: make a better one validation. r can be empty and will not be parsed further
        data = json.loads(r.text)
        if data["data"]:
            return True
        return False

    def testConnection(self, username, users):
        url = users.getAPIUrl(username)+'/api/v1/configuration'
        hdr = { 'Authorization': "Bearer "+users.getUserAccessToken(username) }

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        text = response.read()
        # TODO: make a better one validation. r can be empty and will not be parsed further
        data = json.loads(text.decode('utf-8'))
        if data["data"]:
            return True
        return False