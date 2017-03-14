# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

class SessionGoogle:
    def __init__(self, login, pwd):
        url_login = "https://accounts.google.com/ServiceLogin"
        url_auth = "https://accounts.google.com/ServiceLoginAuth"

        self.ses = requests.session()
        login_html = self.ses.get(url_login)
        soup_login = BeautifulSoup(login_html.content, "lxml").find('form').findAll('input')
        my_dict = {}
        for u in soup_login:
            if u.has_attr('value'):
                my_dict[u['name']] = u['value']

        my_dict['Email'] = login
        my_dict['Passwd'] = pwd
        self.ses.post(url_auth, data=my_dict)

    def get(self, URL):
        return self.ses.get(URL).text

class SessionMicrosoft:
    def __init__(self, login, pwd):
        url_login = "https://login.live.com/"

        self.ses = requests.session()
        login_html = self.ses.get(url_login)
        soup_login = BeautifulSoup(login_html.content, "lxml").find('form').findAll('input')
        my_dict = {}
        for u in soup_login:
            if u.has_attr('value'):
                my_dict[u['name']] = u['value']

        my_dict['i0116'] = login
        my_dict['i0118'] = pwd
        self.ses.post(url_login, data=my_dict)

    def get(self, URL):
        return self.ses.get(URL).text