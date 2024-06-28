from typing import Tuple, List, Dict, Any

from app.plugins import _PluginBase

from .client import PyNUTClient

class NutClient(_PluginBase):
    # 插件名称
    plugin_name = "ups状态api"
    # 插件描述
    plugin_desc = "给homepage使用的ups状态"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/honue/MoviePilot-Plugins/main/icons/shortcut.jpg"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "lwgm"
    # 作者主页
    author_url = ""
    # 插件配置项ID前缀
    plugin_config_prefix = "NutClient_"
    # 加载顺序
    plugin_order = 20
    # 可使用的用户级别
    auth_level = 1    


    def init_plugin(self, config: dict = None) -> None:
        self._enable = config.get("enable") if config.get("enable") else False
        self._url = config.get("url","")
        self._username = config.get("username","")
        self._password = config.get("password","")
        self._upsname = config.get("upsname","")
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
                                            'label': 'ups服务器的地址',
                                            'placeholder': 'ups server url，填入例如: 192.168.2.2',
                                        }
                                    }
                                ]
                            }, {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'upsname',
                                            'label': 'ups名字',
                                            'placeholder': '一般是ups，威联通是qanpups',
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
                                            'label': 'ups monitor用户名',
                                            'placeholder': '一般是admin',
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
                                            'label': 'ups monitor密码',
                                            'placeholder': '一般是123456',
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
设置方法参照homepage的custmapi设置
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
            "username":self._username,
            "upsname":self._upsname
        }
    
    def get_api(self) -> List[Dict[str, Any]]:
        return [{
            "path": "/nutclientapi", 
            "endpoint": self.nutclientapi,
            "methods": ["GET"], 
            "summary": "upsclient的api", 
            "description": "get请求即可"        
        }]

    async def nutclientapi(self)->Dict[str,list|dict]:
        try:
            async with PyNUTClient(host=self._url,login=self._username,password=self._password) as pnc:
                print(f"self._url {self._url},self._username {self._username}, self._password {self._password}")
                __name = await pnc.GetUPSNames()
                __vars = await pnc.GetUPSVars(ups=self._upsname)
        except Exception as e:
            __name = "noname"
            __vars = {}
        name = __name
        vars = __vars
        return {"name":name,"vars":vars} 

    def get_page(self) -> List[dict]:
        pass

    def get_state(self) -> bool:
        return self._enable

    def stop_service(self):
        pass
    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass