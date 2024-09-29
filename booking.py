import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# 从环境变量获取用户名和密码
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

if not username or not password:
    print("请设置 USERNAME 和 PASSWORD 环境变量。")
    exit(1)

# 将日期和开始时间作为输入变量
reservation_date = "10/04/2024"  # 目标日期，格式为 MM/DD/YYYY
start_time_text = "8:00am"        # 开始时间，例如 '8:00am'

# 配置浏览器驱动程序（以 Chrome 为例）
chrome_options = Options()
# 如有需要，可添加无头模式
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)  # 设置显式等待时间

try:
    # 打开登录页面
    driver.get("https://lt.clubautomation.com/")

    # 等待用户名和密码输入框加载
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "login")))
    password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))

    # 输入用户名和密码
    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)

    # 提交登录表单
    password_field.send_keys(Keys.RETURN)

    # 等待登录成功后的元素出现，确认已登录
    # 根据实际情况调整以下等待的元素
    wait.until(EC.presence_of_element_located((By.ID, "main-menu")))

    # 导航到预订页面
    driver.get("https://lt.clubautomation.com/event/reserve-court-new")

    # 等待日期输入框可点击并输入日期
    date_field = wait.until(EC.element_to_be_clickable((By.ID, "date")))
    date_field.clear()
    date_field.send_keys(reservation_date)

    # 选择时长
    duration_radio = wait.until(EC.element_to_be_clickable((By.ID, "interval-120")))
    # 点击父元素以确保交互成功
    duration_parent = duration_radio.find_element(By.XPATH, "./..")
    duration_parent.click()

    # 点击搜索按钮
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "reserve-court-search")))
    search_button.click()

    # 检查是否出现开始时间，最多尝试 100 次，每次间隔 5 秒
    max_attempts = 100
    attempt = 0
    found_start_time = False

    while attempt < max_attempts:
        try:
            # 等待开始时间链接出现（设置较短的等待时间）
            start_time_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{start_time_text}')]"))
            )
            found_start_time = True
            break  # 找到开始时间，退出循环
        except:
            attempt += 1
            print(f"第 {attempt} 次尝试，未找到开始时间 {start_time_text}，5 秒后重试...")
            time.sleep(5)
            # 可根据需要刷新页面或重新点击搜索按钮
            # driver.refresh()
            # search_button.click()

    if not found_start_time:
        print(f"在尝试 {max_attempts} 次后，仍未找到开始时间 {start_time_text}。")
        exit(1)

    # 找到开始时间，点击链接
    start_time_link.click()

    # 确认预订
    confirm_button = wait.until(EC.element_to_be_clickable((By.ID, "confirm")))
    confirm_button.click()

    # 完成预订
    ok_button = wait.until(EC.element_to_be_clickable((By.ID, "button-ok")))
    ok_button.click()

    # 获取预订列表表格
    table_element = wait.until(EC.presence_of_element_located((By.ID, "table-reservation-list")))
    table_html = table_element.get_attribute('outerHTML')

    # 使用 pandas 解析 HTML 表格
    dfs = pd.read_html(table_html)
    reservation_df = dfs[0]

    # 输出预订信息
    print(reservation_df)

except Exception as e:
    print(f"发生错误: {e}")
finally:
    driver.quit()
