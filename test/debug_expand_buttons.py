from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import shutil

def debug_expand_buttons():
    options = webdriver.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    chromedriver_path = shutil.which('chromedriver')
    service = Service(chromedriver_path) if chromedriver_path else None
    driver = webdriver.Chrome(service=service, options=options) if service else webdriver.Chrome(options=options)
    
    try:
        user_id = '6070369404'
        user_url = f'https://xueqiu.com/u/{user_id}'
        driver.get(user_url)
        time.sleep(5)
        
        print(f"页面标题: {driver.title}")
        
        # 查找动态元素
        posts = driver.find_elements(By.CSS_SELECTOR, ".timeline__item, .status-item, [data-type='status']")
        print(f"找到 {len(posts)} 条动态")
        
        if posts:
            post = posts[0]  # 只分析第一条动态
            print(f"\n=== 分析第一条动态 ===")
            
            # 获取初始内容
            initial_text = post.text
            print(f"初始内容长度: {len(initial_text)}")
            print(f"初始内容预览: {initial_text[:200]}...")
            
            # 检查是否包含省略号或截断标识
            truncation_indicators = ['...', '…', '展开', '全文', '更多']
            is_truncated = any(indicator in initial_text for indicator in truncation_indicators)
            print(f"内容是否被截断: {is_truncated}")
            
            # 查找所有可能的可点击元素
            clickable_elements = post.find_elements(By.CSS_SELECTOR, 
                "a, button, span[role='button'], div[role='button'], .clickable, [onclick], [data-action]")
            print(f"\n找到 {len(clickable_elements)} 个可点击元素:")
            
            for i, element in enumerate(clickable_elements):
                try:
                    tag = element.tag_name
                    text = element.text.strip()
                    title = element.get_attribute('title') or ''
                    class_name = element.get_attribute('class') or ''
                    onclick = element.get_attribute('onclick') or ''
                    data_action = element.get_attribute('data-action') or ''
                    
                    print(f"  {i+1}. {tag} - 文本: '{text}' | 标题: '{title}' | 类: '{class_name}' | 点击: '{onclick}' | 动作: '{data_action}'")
                    
                    # 检查是否可能是展开按钮
                    expand_keywords = ['展开', '全文', '更多', 'more', 'expand', 'show', '显示']
                    is_expand_candidate = (
                        any(keyword in text.lower() for keyword in expand_keywords) or
                        any(keyword in title.lower() for keyword in expand_keywords) or
                        any(keyword in class_name.lower() for keyword in ['expand', 'more', 'unfold', 'show']) or
                        any(keyword in onclick.lower() for keyword in expand_keywords) or
                        any(keyword in data_action.lower() for keyword in expand_keywords)
                    )
                    
                    if is_expand_candidate:
                        print(f"    ⭐ 这可能是展开按钮！")
                        
                        # 尝试点击
                        if element.is_displayed() and element.is_enabled():
                            print(f"    正在尝试点击...")
                            try:
                                # 滚动到元素位置
                                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                
                                # 尝试多种点击方式
                                click_methods = [
                                    lambda: element.click(),
                                    lambda: driver.execute_script("arguments[0].click();", element),
                                    lambda: ActionChains(driver).move_to_element(element).click().perform()
                                ]
                                
                                clicked = False
                                for j, click_method in enumerate(click_methods):
                                    try:
                                        click_method()
                                        time.sleep(2)  # 等待内容加载
                                        
                                        # 检查内容是否有变化
                                        new_text = post.text
                                        if len(new_text) > len(initial_text):
                                            print(f"    ✅ 成功展开！方法 {j+1} 有效")
                                            print(f"    内容长度从 {len(initial_text)} 增加到 {len(new_text)}")
                                            print(f"    新内容预览: {new_text[:300]}...")
                                            clicked = True
                                            break
                                        else:
                                            print(f"    方法 {j+1} 无效，内容无变化")
                                    except Exception as click_error:
                                        print(f"    方法 {j+1} 失败: {click_error}")
                                
                                if clicked:
                                    print(f"\n🎉 找到有效的展开方法！")
                                    print(f"有效元素信息:")
                                    print(f"  标签: {tag}")
                                    print(f"  文本: '{text}'")
                                    print(f"  类名: '{class_name}'")
                                    print(f"  选择器建议: {tag}[class*='{class_name.split()[0]}']" if class_name else tag)
                                    break
                                else:
                                    print(f"    ❌ 所有点击方法都无效")
                            except Exception as e:
                                print(f"    ❌ 点击过程出错: {e}")
                        else:
                            print(f"    ❌ 元素不可点击")
                except Exception as e:
                    print(f"  元素 {i+1} 分析失败: {e}")
            
            # 如果没有找到明显的展开按钮，尝试查找包含省略号的元素
            print(f"\n=== 查找包含省略号的元素 ===")
            ellipsis_elements = post.find_elements(By.XPATH, ".//*[contains(text(), '...') or contains(text(), '…')]")
            print(f"找到 {len(ellipsis_elements)} 个包含省略号的元素")
            
            for i, element in enumerate(ellipsis_elements):
                try:
                    print(f"  {i+1}. {element.tag_name} - '{element.text[:50]}...'")
                    
                    # 查找该元素附近的可点击元素
                    parent = element.find_element(By.XPATH, "..")
                    nearby_clickables = parent.find_elements(By.CSS_SELECTOR, "a, button, span[role='button']")
                    
                    for clickable in nearby_clickables:
                        if clickable.is_displayed():
                            print(f"    附近的可点击元素: {clickable.tag_name} - '{clickable.text}'")
                except Exception as e:
                    continue
        
    finally:
        input("\n按回车键关闭浏览器...")  # 暂停以便观察
        driver.quit()

if __name__ == "__main__":
    debug_expand_buttons()