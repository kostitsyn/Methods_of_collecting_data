import scrapy
import re
import json
import sys
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from postsdataparser.items import PostsdataparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']

    def __init__(self, users_num):
        super().__init__()
        self.users_num = users_num
        self.start_urls = ['http://instagram.com/']
        with open('../person.json') as f:
            profile_dict = json.load(f)
        self.inst_login = profile_dict['login']
        self.inst_passwd = profile_dict['password']
        self.inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
        self.header = {'User-Agent': 'Instagram 155.0.0.37.107'}
        self.api_url = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_passwd},
                                 headers={'X-CSRFToken': csrf})

    def user_login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            variables = {
                'count': 12,
                'search_surface': 'follow_list_page'
            }
            url = f'{self.api_url}{j_body["userId"]}/followers/?{urlencode(variables)}'
            yield response.follow(url, callback=self.get_users, headers=self.header)

    def get_users(self, response: HtmlResponse):
        """Получить друзей-подписчиков для последующего скрапинга их контактов."""

        j_body = response.json()
        try:
            j_body['users'][self.users_num-1]
        except IndexError:
            print('Указанное число пользователей превышает реальное количество подписчиков!')
            sys.exit(0)
        else:
            users = j_body['users'][:self.users_num]
        for user in users:
            yield response.follow(f'/{user["username"]}',
                                  callback=self.user_data_parse,
                                  cb_kwargs={'user_data': user})

    def user_data_parse(self, response: HtmlResponse, user_data):
        variables_followers = {
            'count': 12,
            'search_surface': 'follow_list_page'
        }
        url_followers = f'{self.api_url}{user_data["pk"]}/followers/?{urlencode(variables_followers)}'
        yield response.follow(url_followers,
                              callback=self.followers_parse,
                              cb_kwargs={'user_data': user_data,
                                         'variables': deepcopy(variables_followers)},
                              headers=self.header
                              )

        variables_following = {
            'count': 12,
        }
        url_following = f'{self.api_url}{user_data["pk"]}/following/?{urlencode(variables_following)}'
        yield response.follow(url_following,
                              callback=self.following_parse,
                              cb_kwargs={'user_data': user_data,
                                         'variables': deepcopy(variables_following)},
                              headers=self.header
                              )

    def followers_parse(self, response: HtmlResponse, user_data, variables):
        """Парсинг подписчиков."""

        if response.status == 200:
            j_data = response.json()
            if j_data.get('big_list'):
                variables['max_id'] = j_data.get('next_max_id')
                url_followers = f'{self.api_url}{user_data.get("pk")}/followers/?{urlencode(variables)}'
                yield response.follow(url_followers,
                                      callback=self.followers_parse,
                                      cb_kwargs={'user_data': user_data,
                                                 'variables': variables},
                                      headers=self.header
                                      )
            followers = j_data.get('users')
            for follower in followers:
                # Для последующих запросов к БД сохраним дополнительно два поля:
                # владелец аккаунта;
                # отношение рассматриваемого профиля к владельцу аккаунта: подписчик или профиль на который подписаны.
                item = PostsdataparserItem(_id=follower.get('pk'),
                                           owner=user_data.get("username"),
                                           relation='follower',
                                           login=follower.get('username'),
                                           name=follower.get('full_name'),
                                           avatar=follower.get('profile_pic_url'),
                                           follower_data=follower)
                yield item

    def following_parse(self, response:HtmlResponse, user_data, variables):
        """Парсинг на кого подписан."""

        if response.status == 200:
            j_data = response.json()
            if j_data.get('big_list'):
                variables['max_id'] = j_data.get('next_max_id')
                url_followings = f'{self.api_url}{user_data.get("pk")}/following/?{urlencode(variables)}'
                yield response.follow(url_followings,
                                      callback=self.following_parse,
                                      cb_kwargs={'user_data': user_data,
                                                 'variables': variables},
                                      headers=self.header
                                      )
            followings = j_data.get('users')
            for following in followings:
                item = PostsdataparserItem(_id=following.get('pk'),
                                           owner=user_data.get("username"),
                                           relation='following',
                                           login=following.get('username'),
                                           name=following.get('full_name'),
                                           avatar=following.get('profile_pic_url'),
                                           follower_data=following)
                yield item


    def get_csrf_token(self, text):
        csrf = re.findall('csrf_token":"(\w+)"?', text)[0]
        return csrf
