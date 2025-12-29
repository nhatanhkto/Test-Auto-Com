import time
import csv
import requests
from datetime import datetime, timedelta, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains # <--- THÊM CÁI NÀY

# --- CẤU HÌNH ---
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'

# LINK FORM TEST (Bạn thay bằng link thật sau khi test xong)
LINK_FORM = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAADa9laBUQk1OMzJJTE1YVUtHOTZDNTc4N0gzOE9QUS4u'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"
# ----------------

def check_schedule():
    # Để test thì luôn trả về True
    return True 

def human_type(driver, element, text):
    """Hàm giả lập người gõ phím"""
    try:
        # 1. Cuộn đến ô đó
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        
        # 2. Click vào ô để focus (Quan trọng nhất)
        element.click()
        time.sleep(0.5)
        
        # 3. Dùng ActionChains để gõ từng phím
        actions = ActionChains(driver)
        actions.send_keys(text)
        actions.perform()
        print(f"   [OK] Đã gõ: {text}")
    except Exception as e:
        print(f"   [LỖI GÕ PHÍM]: {e}")

def book_rice():
    print("--- CHẾ ĐỘ: HUMAN TYPING (GIẢ LẬP GÕ PHÍM) ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        driver.get(LINK_FORM)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        print("Đã vào Form.")

        # 1. 34 ĐCV
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '34 ĐCV')]")))
            btn.click()
            print("1. Đã chọn 34 ĐCV")
        except:
            print("Lỗi chọn địa điểm")
        time.sleep(1)

        # ======================================================
        # PHẦN QUAN TRỌNG: TÌM VÀ GÕ PHÍM
        # ======================================================
        print("Đang tìm ô nhập liệu...")
        
        # Lấy tất cả các ô input hiển thị trên màn hình
        inputs = driver.find_elements(By.TAG_NAME, "input")
        # Lọc lấy các ô text
        text_inputs = [i for i in inputs if i.get_attribute("type") in ["text", "email", "", None] and i.is_displayed()]
        
        print(f"Tìm thấy {len(text_inputs)} ô nhập liệu.")

        if len(text_inputs) >= 2:
            # Ô thứ 1 là Tên
            print("-> Đang gõ Tên...")
            human_type(driver, text_inputs[0], MY_NAME)
            
            # Ô thứ 2 là Mã
            print("-> Đang gõ Mã...")
            human_type(driver, text_inputs[1], MY_ID)
        else:
            print("!!! KHÔNG TÌM THẤY Ô NHẬP LIỆU !!!")
        
        time.sleep(1)
        # ======================================================

        # 4. Xquang
        try:
            elem = driver.find_element(By.XPATH, "//span[contains(text(), 'Xquang')]")
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            elem.click()
            print("4. Đã chọn Xquang")
        except:
            print("Lỗi chọn khoa")

        # 5. Ăn trưa
        try:
            # Tìm thẻ chứa chữ ăn trưa
            lunch = driver.find_element(By.XPATH, "//span[contains(text(), 'ăn trưa')]")
            lunch.click()
            print("5. Đã chọn Ăn trưa")
        except:
            try:
                lunch = driver.find_element(By.XPATH, "//span[contains(text(), 'Ăn trưa')]") # Viết hoa
                lunch.click()
                print("5. Đã chọn Ăn trưa (Viết hoa)")
            except:
                print("Lỗi chọn Ăn trưa")

        time.sleep(2)

        # GỬI
        print("Chuẩn bị Gửi...")
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            btn.click()
            print("=> ĐÃ BẤM GỬI!")
        except:
            btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            btn.click()
            print("=> ĐÃ BẤM SUBMIT!")
        
        print("Đang chờ kết quả 15 giây...")
        time.sleep(15)
        
        driver.save_screenshot("evidence.png")
        print("=> ĐÃ CHỤP ẢNH MÀN HÌNH")

    except Exception as e:
        print(f"[LỖI]: {e}")
        driver.save_screenshot("evidence.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    book_rice()
