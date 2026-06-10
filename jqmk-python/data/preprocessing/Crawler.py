from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def crawler():
    print('爬取开始')
    # 设置Chrome选项
    chrome_options = Options()

    # 指定ChromeDriver的路径
    service = Service('C:\Program Files\chromedriver-win64\chromedriver.exe')

    # 使用Selenium初始化Chrome浏览器
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 将窗口移动到左上角并最大化
    driver.set_window_position(0, 0)
    driver.maximize_window()

    # 打开目标网页并登录
    login_url = 'http://192.168.60.32/login'
    driver.get(login_url)

    # 等待并找到用户名输入框
    time.sleep(5)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-input__inner[placeholder='请输入用户名']")))
    driver.find_element(By.CSS_SELECTOR, "input.el-input__inner[placeholder='请输入用户名']").send_keys('宗鹏成')

    # 等待并找到密码输入框
    driver.find_element(By.CSS_SELECTOR, "input.el-input__inner[placeholder='请输入密码']").send_keys('Leaniot@321')

    # 等待并点击登录按钮
    driver.find_element(By.CLASS_NAME, 'login-btn').click()

    # report_url = 'http://192.168.60.32/reprot/normalReport/FineReport_safeManager/金桥三违信息表'
    # driver.get(report_url)

    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, '#item0 .open-btn').click()
    time.sleep(5)
    driver.find_element(By.XPATH, '//div[@class="menu-item"][span[text()="安全管理"]]').click()
    time.sleep(5)
    driver.find_element(By.XPATH, '//span[text()="违章汇总表"]').click()


    # 切换到iframe
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe#show-iframe")
    driver.switch_to.frame(iframe)

    '''
    driver.find_element(By.CSS_SELECTOR, 'div[widgetname="TRAINSTARTDATE"] .fr-trigger-btn-up').click()

    # iframe操作完成，切回主文档
    # driver.switch_to.default_content()

    # 计算昨天的日期
    yesterday = (datetime.now() - timedelta(1))
    yesterday_day = yesterday.day
    yesterday_day_str = str(yesterday_day)

    # driver.find_element(By.XPATH, f"//td[@class='available' and text()='{yesterday_day}']").click()

    # js = "document.getElementsByClassName('.fr-trigger-texteditor').removeAttribute('readonly');"
    js = """
    var elements = document.getElementsByClassName('fr-trigger-texteditor');
    if(elements.length > 0) {
        elements[0].removeAttribute('readonly');
    }
    """
    driver.execute_script(js)
    js = "document.getElementsByClassName('fr-trigger-texteditor')[0].value = '2024-08-16';"
    driver.execute_script(js)
    time.sleep(2)

    # 关闭日期选择器（如果需要的话）
    start_date_input.send_keys(Keys.RETURN)

    # 然后你可以继续执行其他操作，例如点击“查询”按钮
    query_button = driver.find_element(By.CSS_SELECTOR, 'div[widgetname="BUTTON0_C"] button')
    query_button.click()
    
    '''
    #
    # # 使用Selenium获取页面的完整HTML
    # html = driver.page_source
    #
    # # 使用Pandas从HTML中解析表格数据
    # tables = pd.read_html(html)
    #
    # tables_df = pd.DataFrame(tables)

    time.sleep(5)
    # 获取页面HTML
    html = driver.page_source

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'id': '0', 'class': 'x-table'})

    if table:
        rows = table.find_all('tr')
        data1 = []
        data2 = []
        for row in rows[1:3]:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols[0:]]
            data1.append(cols)
        for row in rows[3:]:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols[0:]]
            data2.append(cols)

        # 将数据保存为CSV文件
        data1_df = pd.DataFrame(data1)
        data2_df = pd.DataFrame(data2)
        data1_df_dp = data1_df.iloc[:, 1:]
        data1_df_dp = data1_df_dp.T
        data1_df_dp.reset_index(drop=True, inplace=True)
        data1_df_dp = data1_df_dp.T
        data2_df_dp = data2_df.iloc[:,:-1]
        data_df = pd.concat([data1_df_dp, data2_df_dp], axis=0)
        data_df_output = data_df.iloc[1:, :].reset_index(drop=True)
        data_df_output.columns = data_df.iloc[0]
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        # yesterday = '2025-12-19'
        filtered_df = data_df_output[data_df_output['违章日期'] == yesterday]
        # 关闭浏览器
        driver.quit()
        print('爬取完成')
        return filtered_df
    else:
        print("未找到表格")
        # 关闭浏览器
        driver.quit()
        return None


if __name__ == "__main__":
    crawler()