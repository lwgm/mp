from typing import Tuple, List, Dict, Any
from asyncio import create_task, gather
from app.plugins import _PluginBase

from .qnap import Qnap as getqnap
class QnapMagie(_PluginBase):
    # 插件名称
    plugin_name = "威联通相册api"
    # 插件描述
    plugin_desc = "给homepage使用的威联通相册数据"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/honue/MoviePilot-Plugins/main/icons/shortcut.jpg"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "lwgm"
    # 作者主页
    author_url = ""
    # 插件配置项ID前缀
    plugin_config_prefix = "QnapMagie_"
    # 加载顺序
    # 可使用的用户级别
    auth_level = 1   

    def init_plugin(self, config: dict = None) -> None:
        self._enable = config.get("enable") if config.get("enable") else False
        self._url = config.get("url","")
        self._username = config.get("username","")
        self._password = config.get("password","")

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 2
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enable',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            }
                        ]
                    },{'component': 'VRow',
                        'content': [
                         {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'url',
                                            'label': '服务器地址加端口',
                                            'placeholder': '如http://192.168.2.2:5000',
                                        }
                                    }
                                ]
                            },{
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'username',
                                            'label': '登录名',
                                            'placeholder': '',
                                        }
                                    }
                                ]
                            },{
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'password',
                                            'label': '登录密码',
                                            'placeholder': '',
                                        }
                                    }
                                ]
                            }
                        ]
                    },{
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': """
这个登录账号不要开启双因素，url处输入完整的地址，如：http://192.168.2.2:5000
api地址是
"""
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enable": self._enable,
            "url": self._url,
            "password": self._password,
            "username":self._username
        }  


    async def getqumagie(self)->Dict[str,str]:
        data = [
            ("/qumagie/api/v1/list/mediaCount",{"h":"3"}),
            ("/qumagie/api/list.php",{"t":"facesCount"}),
            ("/qumagie/api/v1/list/locations",{"c":"37","lang":"SCH"})
        ]   
        r_json = {}
        q = getqnap(self._url,self._username,self._password)
        tasks = [create_task(q.post(api=api,data=p)) for api, p in data]
        results = await gather(*tasks)
        try:
            rj1 = await results[0].json()
            r_json["photocount"] = rj1["photoCount"]
            r_json["videocount"] = rj1["videoCount"]
            rj2 = await results[1].json()
            r_json["personcount"] = str(rj2["DataCount"])
            rj3 = await results[2].json()
            r_json["geocout"] = str(len(rj3["DataList"]))
        except Exception as _:
            ...
        return r_json

    def get_api(self) -> List[Dict[str, Any]]:
        return [{
            "path": "/getqumagie", 
            "endpoint": self.getqumagie,
            "methods": ["GET"], 
            "summary": "威联通qumagie的api", 
            "description": "get请求即可"        
        }]

    def get_page(self) -> List[dict]:
        pass

    def get_state(self) -> bool:
        return self._enable

    def stop_service(self):
        pass
    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass