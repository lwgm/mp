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
        if "http://" or "https://" in url:
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
        async with lock: 
            r = await self.__session.post(url=self.__baseurl+"/qumagie/api/v1/list/mediaCount",data = {"h":"3","sid":self.__sid})
            rj = await r.json()
            if rj["status"] == 98:
                await self._login()
            else:
                ...  
        data["sid"] = self.__sid      
        resp = await self.__session.post(url=self.__baseurl+api,data=data)
        return resp   