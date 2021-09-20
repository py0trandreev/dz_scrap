import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    url_api_base = 'https://i.instagram.com/api/v1/friendships'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.insta_login = kwargs['login']
        self.insta_pass = kwargs['password']
        self.user_parse= kwargs['user_to_parse'] #'user_to_parse'=list
        print()


    def parse(self, response: HtmlResponse, **kwargs):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.insta_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pass},
                                 headers={'X-CSRFToken': csrf,
                                          'User-Agent':'Instagram 155.0.0.37.107'})

    def user_login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            for i in self.user_parse:
                yield response.follow(f'/{i}',
                                      callback=self.parse_data_followers,
                                      cb_kwargs={'username': i})


    def parse_data_followers(self, response: HtmlResponse, username): #username - 2х анализируемых пользователя
        user_id = self.fetch_user_id(response.text, username)

        url_followers = f'{self.url_api_base}/{user_id}/followers/?count=12&max_id=12&search_surface=follow_list_page'
        url_following = f'{self.url_api_base}/{user_id}/followers/?count=12&max_id=12'
        yield response.follow(url_followers,
                              callback=self.parse_followers,
                              cb_kwargs={'username': username,
                                         'user_id': user_id},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        yield response.follow(url_following,
                              callback=self.parse_following,
                              cb_kwargs={'username': username,
                                         'user_id': user_id},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def parse_followers(self, response: HtmlResponse, username, user_id): #username - 2х анализируемых пользователей
        print()
        j_data=response.json()

        if j_data.get('next_max_id'):
            max_id = j_data['next_max_id']
            url_followers = f'{self.url_api_base}/{user_id}/followers/?count=12&max_id={max_id}&search_surface=follow_list_page'
            if response.status == 200:
                yield response.follow(
                    url_followers,
                    callback=self.parse_followers,
                    cb_kwargs={'username': username,
                               'user_id': user_id},
                    headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        followers = j_data.get('users') #List of user-followers of our both users
        for follower_dict in followers:
            #имя пользователя-подписчика (у наших 2-х пользователей)
            follower_username = follower_dict["username"]
            #ссылка на пользователя-подписчика
            url_usr_follower = f'{self.start_urls[0]}/{follower_username}'
            if response.status == 200:
                yield response.follow(
                    url_usr_follower,
                    callback=self.get_id_follower,
                    cb_kwargs={"username":username, #Наш основной пользователей, на чьей странице мы находимся
                               "user_id":user_id,   # его ID
                               "follower_username":follower_username, #имя пользователя-подписчика
                               "follower_dict":follower_dict})        #данные пользователя-подписчика

    def get_id_follower(self, response: HtmlResponse, username, user_id, follower_username, follower_dict):
        id_follower=self.fetch_user_id(response.text, follower_username)
        item=InstaparserItem(
            user=username,
            user_id=user_id,
            user_status='follower',
            f_username=follower_username,
            id_f=id_follower,
            f_user_photo=follower_dict['profile_pic_url'])

        yield item
        print()


    def parse_following(self, response: HtmlResponse, username, user_id): # username - 2х анализируемых пользователей
        j_data = response.json()

        if j_data.get('next_max_id'):
            max_id = j_data['next_max_id']
            url_following = f'{self.url_api_base}/{user_id}/followers/?count=12&max_id={max_id}'

            if response.status == 200:
                yield response.follow(
                    url_following,
                    callback=self.parse_following,
                    cb_kwargs={'username': username,
                               'user_id': user_id},
                    headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        followings = j_data.get('users')  # List of user-followers of our both users
        for following_dict in followings:
            # имя пользователя на кот.подписаны наши 2-е пользователей
            following_username = following_dict["username"]
            # ссылка на него
            url_usr_following = f'{self.start_urls[0]}/{following_username}'

            if response.status == 200:
                yield response.follow(
                    url_usr_following,
                    callback=self.get_id_following,
                    cb_kwargs={"username": username,  # Наш основной пользователей, на чьей странице мы находимся
                               "user_id": user_id,  # его ID
                               "following_username": following_username,  # имя пользователя на которого подписаны
                               "following_dict": following_dict})  # данные этого пользователя'

    def get_id_following(self, response: HtmlResponse, username, user_id, following_username, following_dict):
        id_following=self.fetch_user_id(response.text, following_username)
        item=InstaparserItem(
            user=username,
            user_id=user_id,
            user_status='following',
            f_username=following_username,
            id_f=id_following,
            f_user_photo=following_dict['profile_pic_url'])

        yield item
        print()




    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')