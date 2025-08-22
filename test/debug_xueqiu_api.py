import requests
import time
import random

def test_xueqiu_apis():
    session = requests.Session()
    
    # 设置完整的headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://xueqiu.com/',
        'Origin': 'https://xueqiu.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 使用你提供的最新cookie
    cookie_string = 'cookiesu=581740032131147; smidV2=202502201415318bea766c8fd72efec06eb3f5fada28080082472d8a91c96a0; device_id=1866b6a72fe75d41349a48b883d582da; bid=3b0d06c60275f6d0cbbc2b5921e72d41_m7tulvzx; __utmz=1.1741054016.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); xq_is_login=1; u=3160217153; Hm_lvt_1db88642e346389874251b5a1eded6e3=1754964122,1754990431,1755054540,1755134460; HMACCOUNT=F47B80BFC3A814EF; snbim_minify=true; __utmc=1; __utma=1.1481200991.1741054016.1755673857.1755745994.55; __utmt=1; __utmb=1.7.10.1755745994; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1755747331; .thumbcache_f24b8bbe5a5934237bbc0eda20c1b6e7=An/nvFl2D/EQR/oLPTWFQf1HCNFks2bnXEi/mHiFmabLwQEbPW15ejditkyQ0X5wBjEGpk6yBSriQiEn7kVgbw%3D%3D; ssxmod_itna=1-Qq_OiKYvq02hkDhrbG8fGR0bDQDRlDl4BtQD2DIuq7=GFtDCODIGLP7Qr_vdDk7KnLbX5Ztef7pehYDGN4a4xiNDAc40iDC3WdDn0GqT_CfDcohqNbiYnhhCz96dl8fstARhIt84y1NSmuXyUdNI4xGI_BKDb4DyDGtQDG=I4qGGR4GwDGoD34DiDDpdxDUbveqD7xnQMQWe2DRYIeWDm4q5ZDqDmLHDnEcTTPWeM_aDfRrW3PwkDY=DQMOQlDWDjfHWzKGyCeGW8bTUgKGuY/2kGOWTrPwXkLLItALi4LhifBt47Yhg4fz1gDMGDAEYxmqehsAgYjEzjoQDDfiDKMO2UiGze_2OtngYcr29QGIY5KlmInwenmAWKtlDtBR80m4tDI0w3lGUlGxnpPemlpGenq1SIwCXeYD; ssxmod_itna2=1-Qq_OiKYvq02hkDhrbG8fGR0bDQDRlDl4BtQD2DIuq7=GFtDCODIGLP7Qr_vdDk7KnLbX5Ztef7pehYDDPbKhKWODGaYWwSqKDBLPD8Bi6a6eWN0g0FKC45IDweeSz73aKWp91AHfh5QAdKtijfK0LUiijxVkUM/4Xqoix4Af4tz03tbDQg8OGRzxND5wXiOnTP2d6HACQ3uMLflj0rN70H0lnNPuLHNlLF5Yyr=_yMtcdO50XsMocT2CQrrCiv=jL50nDYvLcH5ZhF61S24M2TpmiREnXrXk2sZSt4fGkNqdyaNDT/4fd_Swf9bkeB/eqZ0TP94xShgK02DntDctIIGzFeNDsYiVDWa/FHzpZf5FU973q1jvxro4S_KoysYn_WBdUa_7EgGyDq7PB_Pwqab9FSpuzT/9RvfyU7e4fvvFeGCn0inxucXDcx3nXQm77D5vTEf0TcTTsihIOqPTBeB780xrwZ0bdSxpQ_GzGHY4_3T148gKnxAYSY3kI9GtFm3pHy7TZ_Hxww97OU9qDpHmQGQvPIKtkvt5uhZQ4rvHBvaSfzFeecTO39EFoAkrO4C5qBs4x54rU2ZUq2aQiXgrPUkO6QFM26rtXgGDD'
    
    # 解析cookie字符串为字典
    cookies = {}
    for item in cookie_string.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value
    
    session.headers.update(headers)
    session.cookies.update(cookies)
    
    # 测试不同的API接口
    test_apis = [
        {
            'name': 'v4 API',
            'url': 'https://xueqiu.com/v4/statuses/user_timeline.json',
            'params': {'user_id': '6070369404', 'count': 5}
        },
        {
            'name': 'v5 API with user_id',
            'url': 'https://stock.xueqiu.com/v5/stock/timeline/statuses.json',
            'params': {'user_id': '6070369404', 'count': 5, 'source': 'user'}
        },
        {
            'name': 'v5 API with symbol_id',
            'url': 'https://stock.xueqiu.com/v5/stock/timeline/statuses.json',
            'params': {'symbol_id': '6070369404', 'count': 5, 'source': 'user'}
        },
        {
            'name': 'Alternative v4 API',
            'url': 'https://xueqiu.com/statuses/user_timeline.json',
            'params': {'user_id': '6070369404', 'count': 5}
        }
    ]
    
    for api in test_apis:
        print(f"\n测试 {api['name']}:")
        print(f"URL: {api['url']}")
        print(f"参数: {api['params']}")
        
        try:
            response = session.get(api['url'], params=api['params'])
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"原始响应内容: {repr(response.text[:500])}")
            
            if response.status_code == 200:
                # 检查响应内容
                if response.text.strip():
                    try:
                        data = response.json()
                        print(f"成功解析JSON！数据: {str(data)[:200]}...")
                        if 'statuses' in data:
                            print(f"找到 {len(data['statuses'])} 条状态")
                    except ValueError as e:
                        print(f"JSON解析失败: {e}")
                        print(f"响应可能是HTML或其他格式")
                        # 检查是否包含特定的反爬虫标识
                        if 'aliyun_waf' in response.text:
                            print("检测到阿里云WAF反爬虫机制")
                        elif 'renderData' in response.text:
                            print("检测到雪球的特殊响应格式")
                else:
                    print("响应为空")
            else:
                print(f"失败！响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"异常: {e}")
        
        # 添加随机延迟
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    test_xueqiu_apis()