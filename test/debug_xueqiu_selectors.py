from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import shutil

def debug_xueqiu_selectors():
    options = webdriver.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 使用系统ChromeDriver
    chromedriver_path = shutil.which('chromedriver')
    service = Service(chromedriver_path) if chromedriver_path else None
    driver = webdriver.Chrome(service=service, options=options) if service else webdriver.Chrome(options=options)
    
    try:
        user_id = '6070369404'
        user_url = f'https://xueqiu.com/u/{user_id}'
        driver.get(user_url)
        time.sleep(5)
        
        print(f"页面标题: {driver.title}")
        
        # 查找所有可能的动态容器
        possible_selectors = [
            ".timeline__item",
            ".status-item", 
            "[data-type='status']",
            ".timeline-item",
            ".feed-item",
            ".status",
            "article",
            ".post"
        ]
        
        posts = []
        for selector in possible_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ 找到 {len(elements)} 个元素，选择器: {selector}")
                    posts = elements
                    break
                else:
                    print(f"❌ 选择器无效: {selector}")
            except Exception as e:
                print(f"❌ 选择器错误 {selector}: {e}")
        
        if posts:
            print(f"\n分析前3个动态元素的结构:")
            for i, post in enumerate(posts[:3]):
                print(f"\n=== 动态 {i+1} ===")
                print(f"标签名: {post.tag_name}")
                print(f"类名: {post.get_attribute('class')}")
                print(f"ID: {post.get_attribute('id')}")
                print(f"HTML结构: {post.get_attribute('outerHTML')[:300]}...")
                
                # 查找所有子元素
                children = post.find_elements(By.CSS_SELECTOR, "*")
                print(f"子元素数量: {len(children)}")
                
                # 查找可能包含时间的元素
                time_candidates = []
                for child in children:
                    text = child.text.strip()
                    if any(keyword in text.lower() for keyword in ['分钟', '小时', '天', '月', '年', ':', '-', 'ago']):
                        time_candidates.append((child.tag_name, child.get_attribute('class'), text))
                
                if time_candidates:
                    print("可能的时间元素:")
                    for tag, cls, text in time_candidates:
                        print(f"  - {tag}.{cls}: {text}")
        else:
            print("❌ 未找到任何动态元素")
            print("页面源码片段:")
            print(driver.page_source[:1000])
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_xueqiu_selectors()