import time
import csv
import requests
from datetime import datetime, timedelta, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# ======================================================
# THAY 2 LINK CỦA BẠN VÀO GIỮA DẤU NHÁY ĐƠN DƯỚI ĐÂY:
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'
LINK_FORM = 'https://forms.gle/BgakdNVFvbYUWQiQA'
# ======================================================

def get_vietnam_time():
    # GitHub Server dùng giờ UTC, ta phải cộng 7 tiếng để ra giờ VN
    utc_now = datetime.now(timezone.utc)
    vn_now = utc_now + timedelta(hours=7)
    return vn_now.strftime("%d/%m/%Y")

def check_schedule():
    print("--- BẮT ĐẦU KIỂM TRA LỊCH ---")
    try:
        response = requests.get(LINK_CSV)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
        
        today_vn = get_vietnam_time()
        print(f"Hôm nay (Giờ VN): {today_vn}")

        reader = csv.DictReader(lines)
        for row in reader:
            # So sánh ngày
            if row['Ngay'] == today_vn:
                print(f"-> Tìm thấy lịch ngày {today_vn}: Trạng thái '{row['DiLam']}'")
                if row['DiLam'].lower().strip() == 'x':
                    return True
                else:
                    return False
        
        print("-> Không thấy ngày hôm nay trong file Excel. Mặc định: NGHỈ.")
        return False
    except Exception as e:
        print(f"Lỗi đọc file CSV: {e}")
        return False

def run_google_form():
    print("--- BẮT ĐẦU CHẠY ROBOT ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Chạy ngầm
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(LINK_FORM)
        time.sleep(3) # Chờ web load
        
        print("Đã vào form...")

        # Tìm tất cả ô nhập liệu (Google Form thường là input text)
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        
        if len(inputs) > 0:
            inputs[0].send_keys("Nguyen Van Test") # Điền tên giả
            print("- Đã điền tên")
        
        if len(inputs) > 1:
            inputs[1].send_keys("MS123456") # Điền mã giả
            print("- Đã điền mã")

        # Tìm nút Gửi (Google Form nút Gửi là span có chữ Gửi hoặc Submit)
        # Cách tìm thông minh: tìm thẻ có chứa chữ "Gửi"
        try:
            submit_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Gửi')]")
            submit_btn.click()
        except:
            # Nếu dùng tiếng Anh thì tìm chữ Submit
            submit_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Submit')]")
            submit_btn.click()

        print("=> ĐÃ BẤM GỬI THÀNH CÔNG!")
        time.sleep(2)

    except Exception as e:
        print(f"Lỗi khi điền form: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if check_schedule():
        run_google_form()
    else:
        print("=> Hôm nay không có lịch hoặc được nghỉ. Không chạy.")
