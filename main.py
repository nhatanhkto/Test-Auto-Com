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

# --- CẤU HÌNH THÔNG TIN CỦA BẠN ---
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'
LINK_FORM = 'https://forms.office.com/r/ZjK2MqRCUw'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"
# ----------------------------------

def get_vietnam_time():
    # Giờ server GitHub là UTC, cộng 7 để ra giờ VN
    utc_now = datetime.now(timezone.utc)
    vn_now = utc_now + timedelta(hours=7)
    return vn_now.strftime("%d/%m/%Y")

def check_schedule():
    print("--- KIỂM TRA LỊCH TRÌNH ---")
    try:
        response = requests.get(LINK_CSV)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
        
        today_vn = get_vietnam_time()
        print(f"Hôm nay là: {today_vn}")

        reader = csv.DictReader(lines)
        for row in reader:
            if row['Ngay'] == today_vn:
                status = row['DiLam'].lower().strip()
                if status == 'x' or status == 'co':
                    print(f"-> Lịch ghi '{status}'. => CÓ ĐI LÀM.")
                    return True
                else:
                    print(f"-> Lịch ghi '{status}'. => NGHỈ.")
                    return False
        
        print("-> Không thấy ngày hôm nay trong file Excel. Mặc định: NGHỈ.")
        return False
    except Exception as e:
        print(f"Lỗi đọc lịch: {e}")
        return False

def book_rice():
    print("--- BẮT ĐẦU ĐĂNG KÝ CƠM ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Giả lập màn hình lớn để tránh giao diện mobile bị ẩn nút
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get(LINK_FORM)
        # Chờ form load xong (đợi thẻ body hiện ra)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5) 
        print("Đã vào Form Microsoft.")

        # --- 1. Chọn Nơi làm việc: 34 ĐCV ---
        # Tìm thẻ span chứa chữ "34 ĐCV"
        try:
            place_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '34 ĐCV')]")))
            place_btn.click()
            print("- Đã chọn: 34 ĐCV")
        except:
            print("! Lỗi chọn địa điểm, thử tìm chính xác...")
            driver.find_element(By.XPATH, "//*[text()='34 ĐCV']").click()

        time.sleep(1)

        # --- 2 & 3. Điền Họ tên và Mã NV ---
        # Tìm tất cả các ô nhập liệu text
        text_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        
        # Microsoft Form thường xếp theo thứ tự câu hỏi
        # Ô 1: Họ tên, Ô 2: Mã NV (dựa theo ảnh của bạn)
        if len(text_inputs) >= 2:
            text_inputs[0].send_keys(MY_NAME)
            print(f"- Đã điền tên: {MY_NAME}")
            
            text_inputs[1].send_keys(MY_ID)
            print(f"- Đã điền mã: {MY_ID}")
        else:
            print("!!! CẢNH BÁO: Không tìm thấy đủ ô nhập liệu.")

        time.sleep(1)

        # --- 4. Chọn Bộ phận: Xquang ---
        # Vì danh sách dài, cần cuộn xuống hoặc tìm kỹ
        try:
            dept_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Xquang')]")
            driver.execute_script("arguments[0].scrollIntoView();", dept_btn) # Cuộn đến nơi
            time.sleep(1)
            dept_btn.click()
            print("- Đã chọn: Xquang")
        except Exception as e:
            print(f"! Lỗi chọn khoa: {e}")

        # --- 5. Đăng ký ăn trưa ---
        try:
            lunch_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'ăn trưa')]")
            lunch_btn.click()
            print("- Đã chọn: Ăn trưa")
        except:
            print("! Không thấy nút ăn trưa (có thể form thay đổi?)")

        time.sleep(1)

        # --- Gửi Form ---
        # Tìm nút Gửi (Submit)
        try:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            submit_btn.click()
            print("=> ĐÃ BẤM GỬI!")
        except:
            # Phòng trường hợp tiếng Anh
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            submit_btn.click()
            print("=> ĐÃ BẤM SUBMIT!")
        
        # Chờ xác nhận
        time.sleep(5)
        print("Hoàn tất quy trình.")

    except Exception as e:
        print(f"Lỗi nghiêm trọng: {e}")
        # Chụp màn hình lỗi để debug (xem trong Artifacts nếu cần - nâng cao)
    finally:
        driver.quit()

if __name__ == "__main__":
    if check_schedule():
        book_rice()
    else:
        print("Hôm nay nghỉ, tắt máy.")
