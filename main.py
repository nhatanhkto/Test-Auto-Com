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

# --- CẤU HÌNH ---
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'
LINK_FORM = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAADa9laBUQk1OMzJJTE1YVUtHOTZDNTc4N0gzOE9QUS4u'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"
# ----------------

def get_vietnam_time():
    utc_now = datetime.now(timezone.utc)
    vn_now = utc_now + timedelta(hours=7)
    return vn_now.strftime("%d/%m/%Y")

def check_schedule():
    return True # Luôn chạy để test

# HÀM MỚI: Cưỡng ép điền dữ liệu bằng JavaScript
def force_fill(driver, element, value):
    # Cách 1: Click và gõ thường
    try:
        element.click()
        element.clear()
        element.send_keys(value)
    except:
        pass
    
    # Cách 2: TIÊM DATA TRỰC TIẾP (Chống trượt)
    # Lệnh này ép trình duyệt nhận giá trị ngay lập tức
    driver.execute_script("arguments[0].value = arguments[1];", element, value)
    # Báo cho web biết là "Tao vừa điền xong rồi đấy" (Trigger event)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)

def book_rice():
    print("--- CHẾ ĐỘ: FORCE FILL (TIÊM CODE) ---")
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
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '34 ĐCV')]"))).click()
            print("1. Chọn 34 ĐCV")
        except:
            driver.execute_script("window.scrollTo(0, 200)")
            driver.find_element(By.XPATH, "//span[contains(text(), '34 ĐCV')]").click()
        time.sleep(1)

        # ==========================================================
        # PHẦN QUAN TRỌNG NHẤT: TÌM VÀ ĐIỀN TÊN (FORCE FILL)
        # ==========================================================
        
        # Chiến thuật: Lấy tất cả các ô input text trên màn hình
        print("Đang quét các ô nhập liệu...")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        
        # Lọc ra các ô input có thể nhập văn bản
        text_inputs = []
        for inp in all_inputs:
            # Kiểm tra xem có phải ô nhập text không
            if inp.get_attribute("type") in ["text", "email", "tel", ""] or inp.get_attribute("type") is None:
                # Và phải đang hiển thị trên màn hình
                if inp.is_displayed():
                    text_inputs.append(inp)

        print(f"Tìm thấy {len(text_inputs)} ô nhập liệu tiềm năng.")

        if len(text_inputs) >= 2:
            # Ô đầu tiên chắc chắn là Tên
            print("-> Đang cưỡng ép điền Tên...")
            force_fill(driver, text_inputs[0], MY_NAME)
            
            # Ô thứ hai chắc chắn là Mã
            print("-> Đang cưỡng ép điền Mã...")
            force_fill(driver, text_inputs[1], MY_ID)
        else:
            # Nếu không tìm thấy theo kiểu danh sách, tìm theo Label cụ thể
            print("(!) Không tìm thấy đủ ô, chuyển sang tìm theo Label...")
            try:
                inp_name = driver.find_element(By.XPATH, "//div[contains(., 'Họ tên')]//input")
                force_fill(driver, inp_name, MY_NAME)
            except: 
                print("Lỗi tìm ô Tên")
                
            try:
                inp_id = driver.find_element(By.XPATH, "//div[contains(., 'Mã nhân viên')]//input")
                force_fill(driver, inp_id, MY_ID)
            except:
                print("Lỗi tìm ô Mã")

        time.sleep(2)
        # ==========================================================

        # 4. Xquang
        elem = driver.find_element(By.XPATH, "//span[contains(text(), 'Xquang')]")
        driver.execute_script("arguments[0].scrollIntoView();", elem)
        elem.click()
        print("4. Chọn Xquang")

        # 5. Ăn trưa
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'ăn trưa')]").click()
        except:
            driver.find_element(By.XPATH, "//span[contains(text(), 'Ăn trưa')]").click()
        print("5. Chọn Ăn trưa")

        time.sleep(2)

        # GỬI
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            btn.click()
            print("=> ĐÃ BẤM GỬI!")
        except:
            btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            btn.click()
            print("=> ĐÃ BẤM SUBMIT!")
        
        print("Đang chờ kết quả 10 giây...")
        time.sleep(10)
        
        driver.save_screenshot("evidence.png")
        print("=> ĐÃ CHỤP ẢNH MÀN HÌNH")

    except Exception as e:
        print(f"[LỖI]: {e}")
        driver.save_screenshot("evidence.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    book_rice()
