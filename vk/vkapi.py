import requests
import json
import math
import time

from .exceptions import VkApiError

MAX_PER_REQ = {
    "wall.get": 100,
    "groups.getById": 500,
    "wall.getComments": 100,
    "groups.getMembers": 1000,
    "users.get": 1000,
}

SLEEP = 0.34


class VkApi:
    def __init__(self, access_token, v="5.52"):
        self.access_token = access_token
        self.v = v

    def request(self, method, parameters):
        url = "https://api.vk.com/method/%s?%s&access_token=%s&v=%s"
        url_with_parameters = url % (method, parameters, self.access_token, self.v)
        while True:
            try:
                response = requests.get(url_with_parameters, timeout=3)
                break
            except requests.exceptions.ReadTimeout:
                continue
        time.sleep(SLEEP)
        print(url_with_parameters)
        return json.loads(response.text)

    @classmethod
    def extract_response(cls, response):
        if "response" in response:
            # sometimes response["response"] can be int. Lets unify it: make it iterable
            if not isinstance(response["response"], (list, dict)):
                response["response"] = [response["response"]]
            if "items" in response["response"]:
                count, items = cls._extract_response_itemstype(response)
            else:
                count, items = cls._extract_response_non_itemstype(response)
        else:
            code, message = cls._extract_response_error(response)
            raise VkApiError(code, message)
        return (count, items)

    @classmethod
    def _extract_response_itemstype(cls, response):
        count = response["response"]["count"]
        items = response["response"]["items"]
        return (count, items)

    @classmethod
    def _extract_response_non_itemstype(cls, response):
        count = len(response["response"])
        items = response["response"]
        return (count, items)

    @classmethod
    def _extract_response_error(cls, response):
        code = response["error"]["error_code"]
        message = response["error"]["error_msg"]
        return (code, message)

    def get_type_request(self, method, parameters, count=None, initial_offset=0):
        result_list_of_items = []
        total_count = self.get_count(method, parameters)
        if not count:
            count = total_count
        max_items_per_request = MAX_PER_REQ[method]
        parameters += "&count=%s" % min(max_items_per_request, count)
        offset = initial_offset
        for i in range(math.ceil(count / max_items_per_request)):
            offset += max_items_per_request
            parameters_with_offset = parameters + "&offset=%s" % offset
            response = self.request(method, parameters_with_offset)
            count, items = self.extract_response(response)
            result_list_of_items.extend(items)
        return total_count, result_list_of_items

    def post_type_request(self, method, parameters):
        response = self.request(method, parameters)
        count, items = self.extract_response(response)
        return count, items

    def make_request(self, method, parameters, **kwargs):
        if method in MAX_PER_REQ:
            response = self.get_type_request(method, parameters, **kwargs)
        else:
            response = self.post_type_request(method, parameters)
        return response

    def get_count(self, method, parameters):
        response = self.request(method, parameters)
        count, items = self.extract_response(response)
        return count
