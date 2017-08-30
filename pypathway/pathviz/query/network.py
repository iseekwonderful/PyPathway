import requests
from threading import Thread
from ..utils import reraise
import sys


class NetworkException(Exception):
    '''
    This is a class handle exceptions occurs while requesting network resource

    Args:
        url: the location of the resource.
        message: the exception message
    '''
    def __init__(self, url, message):
        Exception.__init__(self, message)
        self.url = url


class NetworkMethod:
    '''
    This is a class manage Http request methods.

    Attributes:
        GET: HTTP request method.
        POST: another HTTP request method.
    '''
    GET = 0
    POST = 1


class NetworkRequest:
    '''
    This class provide a stable web request class.

    Args:
        url: the location of the resource.
        method: member of NetworkMethod, GET or POST, aka, 0 or 1.

    Attributes:
        text: The raw result of the request
    '''
    def __init__(self, url, method, binary=False, proxy=None, post_arg=None):
        self.url = url
        self.method = method
        self.binary = binary
        self.proxy = proxy
        self.post_arg = post_arg or {}
        if method == NetworkMethod.GET:
            self.text = self._request_get()
        else:
            self.text = self._request_post()

    def _request_get(self):
        try:
            request = requests.get(self.url, timeout=20, proxies=self.proxy)
            text = request.text
            if self.binary:
                text = request.content
        except Exception as e:
            raise NetworkException(self.url, e)
        else:
            return text

    def _request_post(self):
        self.post_arg['url'] = self.url
        self.post_arg['timeout'] = 20
        self.post_arg['proxies'] = self.proxy
        try:
            request = requests.post(**self.post_arg)
            text = request.text
        except Exception as e:
            raise NetworkException(self.url, e)
        else:
            return text


class MultiThreadNetworkRequest(Thread):
    '''
    This class provide a Thread base class to access network data, and set the result to certain class

    Args:
        url: the location of the resource.
        method: member of NetworkMethod, GET or POST, aka, 0 or 1.
        target: set the result to certain class instance.
        attr: the attr name of a class instance, using setattr(target, attr, result)

    Attributes:
        consider Thread class
    '''
    def __init__(self, url, method, target=None, attr=None,
                 binary=False, callback=None, callback_args=None, proxy=None, error_queue=None):
        Thread.__init__(self)
        self.url = url
        self.method = method
        self.target = target
        self.attr = attr
        self.data = None
        self.binary = binary
        self.callback = callback
        self.callback_args = callback_args
        self.proxy = proxy
        self.error_queue = error_queue

    def run(self):
        try:
            nt = NetworkRequest(url=self.url, method=self.method,
                                binary=self.binary, proxy=self.proxy)
            if self.callback:
                if not self.callback_args:
                    self.callback_args = []
                self.callback_args.insert(0, nt.text)
                self.callback(*self.callback_args)
            else:
                setattr(self.target, self.attr, nt.text)
        except Exception as e:
            if self.error_queue:
                self.error_queue.put((self.url, e))

        #     # print "MNR: NetworkException: {}".format(e.message)
        #     if self.error_queue:
        #         self.error_queue.put((self.url, e.message))
        # except Exception as e:
        #     print("Exception")
        #     if self.error_queue:
        #         self.error_queue.put((self.url, e.message))
