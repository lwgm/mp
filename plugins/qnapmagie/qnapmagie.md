api地址为 http://moviepilot_url:moviepilot_apiport/api/v1/plugin/QnapMagie/getqumagie   
homepage的设置    

- Qumagie Photos:
    widget:
        type: customapi
        url: http://moviepilot_url:moviepilot_apiport/api/v1/plugin/QnapMagie/getqumagie
        refreshInterval: 10000000
        method: GET
        mappings:
        - field: photocount
            label: 照片
        - field: videocount
            label: 视频
        - field: personcount
            label: 人物
        - field: geocout
            label: 足迹