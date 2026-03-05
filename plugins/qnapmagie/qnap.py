from typing import Optional
from abc import ABCMeta
from asyncio import Lock
from base64 import b64encode as bb64encode
from aiohttp import ClientSession
from xmltodict import parse as xmlparse


lock = Lock()
class Singleton(ABCMeta,type):
    # 单线程
    _instances = {}
    def __call__(cls, *args, **kwargs):             
        key = (cls, args, frozenset(kwargs.items()))
        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]

class Qnap(metaclass=Singleton):
    __session = None
    __sid :Optional[str] = None
    __username :Optional[str] = None
    __baseurl :Optional[str] = None
    __password :Optional[str] = None
    def __init__(self,url,username,password):
        self.__session = ClientSession()
        if "http://" in url or "https://" in url:
            self.__baseurl = url
        self.__username = username
        self.__password = password
    async def _login(self):
        data = {
            "user": self.__username,
            "pwd": bb64encode(self.__password.encode('utf-8')).decode('ascii')
        }
        resp = await self.__session.post(url=self.__baseurl+"/cgi-bin/authLogin.cgi",data=data)
        data = xmlparse(await resp.content.read(), force_list=None)['QDocRoot']
        url = self.__baseurl+"/qumagie/api/user.php"
        data = {"a":"login","ssid":data.get("authSid")}
        resp = await self.__session.post(url=url,data=data)
        self.__sid = resp.cookies["QMS_SID"].value

    async def post(self, api, data={}): 
        """
        获取qnap照片信息，报错98后，登录后再获取
        """ 
        if not self.__baseurl:
            return None
        if not self.__sid:
            # Double-checked locking: multiple coroutines may pass the outer
            # check while __sid is None; the inner check inside the lock
            # ensures only the first one performs the actual login.
            async with lock:
                if not self.__sid:
                    await self._login()
        payload = {**data, "sid": self.__sid}
        resp = await self.__session.post(url=self.__baseurl+api, data=payload)
        rj = await resp.json()
        if rj.get("status") == 98:
            async with lock:
                await self._login()
            payload = {**data, "sid": self.__sid}
            resp = await self.__session.post(url=self.__baseurl+api, data=payload)
            rj = await resp.json()
        return rj   