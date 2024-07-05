from typing import List, Tuple, Dict, Any, Optional
from enum import Enum
from re import compile
from asyncio import Protocol, get_running_loop, Future
from asyncio import run as arun
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

from app.plugins import _PluginBase
from app.log import logger
from app import schemas
from app.schemas import NotificationType
from app.core.plugin import PluginManager

class StrEnum(str, Enum):
    value: str
    def __str__(self) -> str:
        return self.value
class LevelType(StrEnum):
        # Emergency:int = 0 # （紧急） - 
        # Alert:int = 1 #（警报） - 
        # Critical:int = 2 #（临界） - 
        # Error:int = 3 #（错误） - 
        # Warning:int = 4 # （警告） - 
        # Notice:int = 5 # （通知） - 
        # Informational:int = 6 # （信息） - 
        # Debug:int = 7 # （调试） -     
        Emergency:str = "Emergency" # （紧急） - 
        Alert:str = "Alert" #（警报） - 
        Critical:str = "Critical" #（临界） - 
        Error:str = "Error" #（错误） - 
        Warning:str = "Warning" # （警告） - 
        Notice:str = "Notice" # （通知） - 
        Informational:str = "Informational" # （信息） - 
        Debug:str = "Debug" # （调试）


class syslog1:
    def __init__(self, pri, times, qnapname, pro, pid, msg, omsg) -> None:
        self.pri = pri
        self.times = times
        self.qnapname = qnapname
        self.pro = pro
        self.pid = pid
        self.msg = msg
        self.omsg = omsg


    def sendevent(self) -> None:
        PluginManager().run_plugin_method(pid="QnapNotify", method="send_notify",qnapsyslog=self)

    @classmethod
    def parse(cls, msg) -> Optional["syslog1"]:
        """
        "<28>Feb  7 19:03:19 TS464C qulogd[19238]: conn log: Users: lwgm, Source IP: 192.168.2.1, Computer name: ---, Connection type: HTTP, Accessed resources: Administration, Action: Login Fail"
        """
        rep = compile(
            "\<(\w+)>(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\w+)\s+(\w+)\[(\d+)\]:\s+"
        )
        m1 = rep.findall(msg)
        rep2 = compile(
            "\<(\w+)>"
        ) # 备用
        m2 = rep2.findall(msg)
        if m1:
            omsg = msg
            pri, times, qnapname, pro, pid = m1[0]
            msg = rep.sub("", msg)
            return cls(pri, times, qnapname, pro, pid, msg, omsg)
        elif m2:
            pri = m2[0]
            return cls(pri,"","","","","",msg)
        else:
            return None

    def __repr__(self) -> str:
        return f"{self.pri} ->{self.times} ->{self.qnapname} ->{self.pro} ->{self.pid} ->{self.msg}"

class TCPServerProtocol(Protocol):
    def __init__(self,f:Future) -> None:
        self.future:Future = f
    def connection_made(self, transport) -> None: ...
    def data_received(self, data) -> None:
        msg = data.decode()
        if msg == "lwgm":
            self.future.set_result(True)
        s = syslog1.parse(msg)
        if s:
            s.sendevent()
        else:
            logger.warning(f"syslog没有解析到消息,收到的信息是 --->{msg}")

    def connection_lost(self, exc: Optional[Exception]) -> None: ...
    def eof_received(self) -> None: ...

class TCPServer:
    @staticmethod
    async def starttcpserver(host, port) -> None:
                      
            loop = get_running_loop()
            future :Future= loop.create_future()
            await loop.create_server(
                lambda: TCPServerProtocol(future), host=str(host), port=port, start_serving=True, reuse_address=True
            )
            logger.info("server has been started")
            await future
            logger.info("server is to stop")


class QnapNotify(_PluginBase):
    """
    根据群晖的webhook通知改写的
    """
    # 插件名称
    plugin_name = "威联通Webhook通知"
    # 插件描述
    plugin_desc = "接收威联通的syslog并转发。"
    # 插件图标
    plugin_icon = "https://github.com/jxxghp/MoviePilot-Plugins/tree/main/icons/Qnap_A.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "lwgm"
    # 作者主页
    author_url = ""
    # 插件配置项ID前缀
    plugin_config_prefix = "QnapNotify_"
    # 加载顺序
    # 可使用的用户级别
    auth_level = 1
    # user define
    _thread :Thread = None
    def init_plugin(self, config: dict = None) -> None:
        self._enabled = config.get("enabled",False)
        self._notify = config.get("notify",False)
        self._msgtype = config.get("msgtype",NotificationType.Manual)
        self._level = config.get("level",LevelType.Notice)
        self._leveldict = {
        "Emergency":0, # （紧急） - 
        "Alert":1, #（警报） - 
        "Critical":2, #（临界） - 
        "Error":3, #（错误） - 
        "Warning":4, # （警告） - 
        "Notice":5, # （通知） - 
        "Informational":6, # （信息） - 
        "Debug":7, # （调试） -              
        }
          

        if self._enabled:
            if not self._thread or not self._thread.is_alive():
                self.start()
        else:
            def send_stop() -> None:
                s = socket(AF_INET, SOCK_STREAM)
                server = ("localhost",63210)
                s.connect(server)
                str1 = "lwgm"
                msg = str1.encode("utf-8")
                s.send(msg)
            send_stop()
                

    def send_notify(self, qnapsyslog:syslog1=None) -> schemas.Response:
        """
        发送通知
        """
        text = qnapsyslog.omsg
        logger.info(f"收到webhook消息啦。。。  {text}")
        if self._enabled and self._notify:
            mtype = NotificationType.Manual
            if self._msgtype:
                mtype = NotificationType.__getitem__(str(self._msgtype)) or NotificationType.Manual
            if int(qnapsyslog.pri) % 8 <= self._leveldict[self._level]:
                self.post_message(title="威联通通知",
                                mtype=mtype,
                                text=text)

        return schemas.Response(
            success=True,
            message="发送成功"
        )        


    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        # 编历 NotificationType 枚举，生成消息类型选项
        MsgTypeOptions = []
        for item in NotificationType:
            MsgTypeOptions.append({
                "title": item.value,
                "value": item.name
            })
        level_options = []
        for item in LevelType:
            level_options.append({
                "title": item.value,
                "value": item.name
            })        
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
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify',
                                            'label': '开启通知',
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'multiple': False,
                                            'chips': True,
                                            'model': 'msgtype',
                                            'label': '消息类型',
                                            'items': MsgTypeOptions
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'multiple': False,
                                            'chips': True,
                                            'model': 'level',
                                            'label': '消息类型',
                                            'items': level_options
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
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
                                            'text': '威联通的配置。'
                                                    '。'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
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
                                            'text': '如。'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "notify": False,
            "msgtype": "",
            "level":"Notice"
        }

    def _run(self) -> None:
        try:
            arun(TCPServer.starttcpserver("0.0.0.0", 63210))
        except Exception as _:
            logger.error(f"报错了",exc_info=True)
    def start(self) -> None:
        self._thread = Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        return

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        """
        退出插件
        """
        pass

    def get_state(self) -> bool:
        return self._enabled

    def get_api(self) -> List[Dict[str, Any]]:
        pass
    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass