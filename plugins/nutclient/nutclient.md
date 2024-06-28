ups服务器的地址，填入例如: 192.168.2.2，ups monitor用户名一般是ups，威联通是qanpups
homepage的设置参照homepage的custmapi设置，例如
- ups:
    id: ups
    icon: ups
    description: 监控ups服务器
    server: my-docker
    container: nasapi
    widget:
        type: customapi
        url: http://xx.xx.xx.xx:3001/api/v1/plugin/NutClient/nutclientapi
        refreshInterval: 10000000
        method: GET
        mappings:
        - field:
            vars: ups.status
            label: 状态
            remap:
            - value: "OL"
                to: 在线
            - any: true
                to: 离线
        - field:
            vars: battery.charge
            label: 电量
        - field:
            vars: ups.load
            label: 负载
            suffix: "%"
        - field:
            vars: battery.voltage
            label: 电压