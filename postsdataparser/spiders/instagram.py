import scrapy
import re

from scrapy.http import HtmlResponse
from urllib.parse import urlencode

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login = 'aleksandr74956'
    inst_passwd = '#PWD_INSTAGRAM_BROWSER:10:1630055380:ATFQAIDgPImjuNZONu0aRePE0gG6YBeAg6p7VeM7v9r7qIliX3TY2iRWxTFTk8FjGNXMOS9JqH1cSkbLaUyuS2yCn9vBISlbFpV0Bj2Oue4r80TStvBsh6WKEo4gGwfdT3jAxe5frKcIID2R'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    header = {'User-Agent': 'Instagram 155.0.0.37.107'}
    users = ['vanyaman1', 'nicky_izh']

    # https://i.instagram.com/api/v1/friendships/6270942197/followers/?count=12&max_id=12&search_surface=follow_list_page
    api_followers_url = 'https://i.instagram.com/api/v1/friendships/'

    # https://i.instagram.com/api/v1/friendships/6270942197/following/?count=12&max_id=12
    api_following_url = 'https://i.instagram.com/api/v1/friendships/'



    def parse(self, response:HtmlResponse):
        csrf = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_passwd},
                                 headers={'X-CSRFToken': csrf})

    def user_login(self, response:HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            for user in self.users:
                yield response.follow(f'/{user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user})

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.get_user_id(response.text, username)
        variables = {
            'id': user_id,
            'first': 12
        }

        # https://i.instagram.com/api/v1/friendships/6270942197/followers/?count=12&max_id=12&search_surface=follow_list_page
        url_followers = f'{self.api_followers_url}{user_id}/followers/?count=12&search_surface=follow_list_page'
        yield response.follow(url_followers,
                              callback=self.followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id},
                              headers=self.header
                              )

        # https://i.instagram.com/api/v1/friendships/6270942197/following/?count=12&max_id=12
        url_following = f'{self.api_following_url}{user_id}/following/?count=12'
        yield response.follow(url_following,
                              callback=self.following_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id},
                              headers=self.header
                              )

    def followers_parse(self, response:HtmlResponse, username, user_id):
        """Парсинг подписчиков."""
        if response.status == 200:
            j_data = response.json()
            followers = j_data.get('users')
            if j_data.get('big_list'):
                spam = j_data.get('next_max_id')

    def following_parse(self, response:HtmlResponse, username, user_id):
        """Парсинг на кого подписан."""
        pass

    def get_csrf_token(self, text):
        csrf = re.findall('csrf_token":"(\w+)"?', text)[0]
        return csrf

    def get_user_id(self, text, username):
        # 43983728396 - Ваня
        # 6270942197 - Коля
        user_id = re.findall(f'"id":"(\d+)","username":"{username}"', text)[0]
        return user_id



