import scrapy
import re

from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from postsdataparser.items import PostsdataparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login = 'aleksandr74956'
    inst_passwd = '#PWD_INSTAGRAM_BROWSER:10:1630055380:ATFQAIDgPImjuNZONu0aRePE0gG6YBeAg6p7VeM7v9r7qIliX3TY2iRWxTFTk8FjGNXMOS9JqH1cSkbLaUyuS2yCn9vBISlbFpV0Bj2Oue4r80TStvBsh6WKEo4gGwfdT3jAxe5frKcIID2R'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    header = {'User-Agent': 'Instagram 155.0.0.37.107'}
    users = ['vanyaman1', 'nicky_izh']
    api_url = 'https://i.instagram.com/api/v1/friendships/'

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
            for user in self.users:
                yield response.follow(f'/{user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user})

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.get_user_id(response.text, username)

        variables_followers = {
            'count': 12,
            'search_surface': 'follow_list_page'
        }
        url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables_followers)}'
        yield response.follow(url_followers,
                              callback=self.followers_parse,
                              cb_kwargs={'user_id': user_id,
                                         'username': username,
                                         'variables': deepcopy(variables_followers)},
                              headers=self.header
                              )

        variables_following = {
            'count': 12,
        }
        url_following = f'{self.api_url}{user_id}/following/?{urlencode(variables_following)}'
        yield response.follow(url_following,
                              callback=self.following_parse,
                              cb_kwargs={'user_id': user_id,
                                         'username': username,
                                         'variables': deepcopy(variables_following)},
                              headers=self.header
                              )

    def followers_parse(self, response: HtmlResponse, user_id, username, variables):
        """Парсинг подписчиков."""

        if response.status == 200:
            j_data = response.json()
            if j_data.get('big_list'):
                variables['max_id'] = j_data.get('next_max_id')
                url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables)}'
                yield response.follow(url_followers,
                                      callback=self.followers_parse,
                                      cb_kwargs={'user_id': user_id,
                                                 'username': username,
                                                 'variables': variables},
                                      headers=self.header
                                      )
            followers = j_data.get('users')
            for follower in followers:
                item = PostsdataparserItem(_id=follower.get('pk'),
                                           owner=username,
                                           relation='follower',
                                           login=follower.get('username'),
                                           name=follower.get('full_name'),
                                           avatar=follower.get('profile_pic_url'),
                                           follower_data=follower)
                yield item

    def following_parse(self, response:HtmlResponse, user_id, username, variables):
        """Парсинг на кого подписан."""

        if response.status == 200:
            j_data = response.json()
            if j_data.get('big_list'):
                variables['max_id'] = j_data.get('next_max_id')
                url_followings = f'{self.api_url}{user_id}/following/?{urlencode(variables)}'
                yield response.follow(url_followings,
                                      callback=self.following_parse,
                                      cb_kwargs={'user_id': user_id,
                                                 'username': username,
                                                 'variables': variables},
                                      headers=self.header
                                      )
            followings = j_data.get('users')
            for following in followings:
                item = PostsdataparserItem(_id=following.get('pk'),
                                           owner=username,
                                           relation='following',
                                           login=following.get('username'),
                                           name=following.get('full_name'),
                                           avatar=following.get('profile_pic_url'),
                                           follower_data=following)
                yield item


    def get_csrf_token(self, text):
        csrf = re.findall('csrf_token":"(\w+)"?', text)[0]
        return csrf

    def get_user_id(self, text, username):
        user_id = re.findall(f'"id":"(\d+)","username":"{username}"', text)[0]
        return user_id



