from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager  # 注释掉这行
import time
import json
import re
import shutil

def test_xueqiu_with_selenium():
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 可选：无头模式（后台运行）
    # options.add_argument('--headless')
    
    # 创建WebDriver实例 - 使用系统ChromeDriver
    try:
        # 方法1：使用系统PATH中的chromedriver
        chromedriver_path = shutil.which('chromedriver')
        if chromedriver_path:
            print(f"使用系统ChromeDriver: {chromedriver_path}")
            service = Service(chromedriver_path)
        else:
            # 方法2：尝试常见的安装路径
            possible_paths = [
                '/usr/local/bin/chromedriver',
                '/opt/homebrew/bin/chromedriver',
                '/usr/bin/chromedriver'
            ]
            
            chromedriver_path = None
            for path in possible_paths:
                if shutil.which(path):
                    chromedriver_path = path
                    break
            
            if chromedriver_path:
                print(f"使用ChromeDriver: {chromedriver_path}")
                service = Service(chromedriver_path)
            else:
                print("未找到ChromeDriver，尝试使用默认设置")
                service = None
        
        # 创建driver
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
            
    except Exception as e:
        print(f"ChromeDriver启动失败: {e}")
        print("请确保已安装ChromeDriver：brew install chromedriver")
        return
    
    try:
        print("正在访问雪球网站...")
        
        # 直接访问用户页面（无需登录）
        user_id = '7820817123'
        user_url = f'https://xueqiu.com/u/{user_id}'
        driver.get(user_url)
        
        # 等待页面加载
        time.sleep(5)
        
        print(f"页面标题: {driver.title}")
        
        # 检查页面是否正常加载
        if "雪球" in driver.title or "xueqiu" in driver.title.lower():
            print("✅ 成功访问雪球用户页面")
            
            # 方法1：通过页面元素获取动态内容
            try:
                # 等待动态内容加载
                wait = WebDriverWait(driver, 10)
                
                # 查找用户动态列表
                posts_container = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".timeline__item, .status-item, [data-type='status']"))
                )
                
                # 获取所有动态元素
                posts = driver.find_elements(By.CSS_SELECTOR, ".timeline__item, .status-item, [data-type='status']")
                
                print(f"找到 {len(posts)} 条动态")
                
                for i, post in enumerate(posts[:5]):  # 只处理前5条
                    try:
                        # 首先尝试展开折叠的内容
                        expand_selectors = [
                            ".expand",
                            ".more", 
                            ".show-more",
                            "[data-action='expand']",
                            ".unfold",
                            ".展开",
                            "button[title*='展开']",
                            "a[title*='展开']",
                            ".timeline-item .expand",
                            ".status-content .expand"
                        ]
                        
                        # 尝试点击展开按钮
                        expanded = False
                        for expand_selector in expand_selectors:
                            try:
                                expand_buttons = post.find_elements(By.CSS_SELECTOR, expand_selector)
                                for button in expand_buttons:
                                    if button.is_displayed() and button.is_enabled():
                                        # 检查按钮文本是否包含展开相关词汇
                                        button_text = button.text.lower()
                                        if any(keyword in button_text for keyword in ['展开', 'more', '更多', 'expand', '全文']):
                                            print(f"找到展开按钮: {button.text}，正在点击...")
                                            driver.execute_script("arguments[0].click();", button)
                                            time.sleep(1)  # 等待内容展开
                                            expanded = True
                                            break
                                if expanded:
                                    break
                            except Exception as e:
                                continue
                        
                        if expanded:
                            print(f"✅ 动态 {i+1} 内容已展开")
                        
                        # 提取动态文本内容
                        text_selectors = [
                            ".timeline-item .text",
                            ".status-content", 
                            ".timeline-item-content",
                            "[data-type='status'] .text",
                            ".feed-item .text",
                            ".content",
                            ".post-content"
                        ]
                        
                        text_element = None
                        text = "无法获取内容"
                        
                        for selector in text_selectors:
                            try:
                                text_element = post.find_element(By.CSS_SELECTOR, selector)
                                text = text_element.text.strip()
                                if text and len(text) > 10:  # 确保获取到有意义的内容
                                    break
                            except:
                                continue
                        
                        # 如果还是找不到，尝试获取整个post的文本
                        if not text or text == "无法获取内容" or len(text) < 10:
                            text = post.text.strip()
                        
                        # 提取时间信息
                        time_text = "未知时间"
                        
                        # 从内容中提取时间信息（雪球的时间通常在内容开头）
                        import re
                        time_patterns = [
                            r'修改于(\d{2}-\d{2} \d{2}:\d{2})',
                            r'发布于(\d{2}-\d{2} \d{2}:\d{2})',
                            r'(\d{2}-\d{2} \d{2}:\d{2})',
                            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})',
                            r'(\d+分钟前)',
                            r'(\d+小时前)',
                            r'(\d+天前)'
                        ]
                        
                        for pattern in time_patterns:
                            match = re.search(pattern, text)
                            if match:
                                time_text = match.group(1)
                                break
                        
                        # 清理内容文本（移除时间信息）
                        clean_text = text
                        for pattern in time_patterns:
                            clean_text = re.sub(pattern, '', clean_text)
                        clean_text = re.sub(r'· 来自雪球.*?$', '', clean_text, flags=re.MULTILINE)
                        clean_text = clean_text.strip()
                        
                        print(f"\n动态 {i+1}:")
                        print(f"时间: {time_text}")
                        print(f"内容: {clean_text[:200]}..." if len(clean_text) > 200 else f"内容: {clean_text}")
                        
                        # 如果是第一条动态，打印更多调试信息
                        if i == 0:
                            print(f"\n调试信息:")
                            print(f"原始文本长度: {len(text)}")
                            print(f"清理后文本长度: {len(clean_text)}")
                            print(f"是否展开: {expanded}")
                        
                    except Exception as e:
                        print(f"解析动态 {i+1} 失败: {e}")
                        # 打印元素结构用于调试
                        try:
                            print(f"元素HTML: {post.get_attribute('outerHTML')[:200]}...")
                        except:
                            pass
                        
            except Exception as e:
                print(f"通过页面元素获取动态失败: {e}")
                
                # 方法2：通过JavaScript API获取数据
                print("\n尝试通过JavaScript API获取数据...")
                try:
                    # 执行JavaScript获取API数据
                    script = f"""
                    return new Promise((resolve) => {{
                        fetch('/v4/statuses/user_timeline.json?user_id={user_id}&count=5', {{
                            method: 'GET',
                            credentials: 'include',
                            headers: {{
                                'Accept': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            }}
                        }})
                        .then(response => response.json())
                        .then(data => resolve(data))
                        .catch(error => resolve({{error: error.toString()}}));
                    }});
                    """
                    
                    result = driver.execute_async_script("""
                    var callback = arguments[arguments.length - 1];
                    """ + script.replace('return new Promise((resolve) => {', '').replace('});', 'callback') + """
                    """)
                    
                    if 'error' not in result:
                        print("✅ 成功通过API获取数据")
                        print(f"API返回数据: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                        
                        if 'statuses' in result:
                            statuses = result['statuses']
                            print(f"\n获取到 {len(statuses)} 条状态:")
                            
                            for i, status in enumerate(statuses[:3]):
                                print(f"\n状态 {i+1}:")
                                print(f"ID: {status.get('id', 'N/A')}")
                                print(f"文本: {status.get('text', 'N/A')[:100]}...")
                                print(f"时间: {status.get('created_at', 'N/A')}")
                                print(f"用户: {status.get('user', {}).get('screen_name', 'N/A')}")
                    else:
                        print(f"API调用失败: {result['error']}")
                        
                except Exception as e:
                    print(f"JavaScript API调用失败: {e}")
                
                # 方法3：直接从页面源码中提取数据
                print("\n尝试从页面源码提取数据...")
                try:
                    page_source = driver.page_source
                    
                    # 查找页面中的JSON数据
                    json_pattern = r'window\.SNB\s*=\s*(\{.*?\});'
                    matches = re.findall(json_pattern, page_source, re.DOTALL)
                    
                    if matches:
                        try:
                            data = json.loads(matches[0])
                            print("✅ 从页面源码中找到数据")
                            print(f"数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        except json.JSONDecodeError:
                            print("页面数据JSON解析失败")
                    else:
                        print("未在页面源码中找到结构化数据")
                        
                except Exception as e:
                    print(f"页面源码解析失败: {e}")
                    
        else:
            print("❌ 页面加载异常，可能被反爬虫拦截")
            print(f"当前URL: {driver.current_url}")
            print(f"页面源码片段: {driver.page_source[:500]}...")
        
    except Exception as e:
        print(f"Selenium测试失败: {e}")
    
    finally:
        print("\n关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    print("开始测试雪球Selenium爬虫...")
    test_xueqiu_with_selenium()
    print("测试完成！")