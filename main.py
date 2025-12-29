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

# --- CẤU HÌNH THÔNG TIN ---
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'
LINK_FORM = 'https://forms.office.com/r/ZjK2MqRCUw'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"
# --------------------------

def get_vietnam_time():
    utc_now = datetime.now(timezone.utc)
    vn_now = utc_now + timedelta(hours=7)
    return vn_now.strftime("%d/%m/%Y")

def check_schedule():
    print("--- 1. KIỂM TRA LỊCH TRÌNH ---")
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
                    print(f"-> Trạng thái '{status}' => CÓ ĐI LÀM.")
                    return True
                else:
                    print(f"-> Trạng thái '{status}' => NGHỈ.")
                    return False
        
        print("-> Không thấy ngày hôm nay trong lịch. Mặc định: NGHỈ.")
        return False
    except Exception as e:
        print(f"Lỗi đọc lịch: {e}")
        return False

def book_rice():
    print("--- 2. BẮT ĐẦU ĐĂNG KÝ CƠM ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Chạy ngầm
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080") # Giả lập màn hình to

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30) # Chờ tối đa 30s
    
    try:
        driver.get(LINK_FORM)
        # Chờ dòng chữ tiêu đề hiện ra để chắc chắn web đã load
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Nơi làm việc')]")))
        time.sleep(5) 
        print("Web đã load xong.")

        # === BƯỚC 1: CHỌN NƠI LÀM VIỆC (34 ĐCV) ===
        try:
            place_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '34 ĐCV')]")))
            place_btn.click()
            print("[OK] Đã chọn: 34 ĐCV")
        except:
            print("[!] Thử lại chọn địa điểm...")
            driver.execute_script("document.evaluate(\"//span[contains(text(), '34 ĐCV')]\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")
        
        time.sleep(1)

        # === BƯỚC 2: ĐIỀN HỌ TÊN (Dựa trên video: Câu hỏi số 2) ===
        # Tìm ô input có aria-label chứa chữ 'Họ tên' (Chính xác nhất)
        try:
            name_input = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'Họ tên')]")
            name_input.send_keys(MY_NAME)
            print(f"[OK] Đã điền tên: {MY_NAME}")
        except:
            # Dự phòng: Tìm div chứa chữ 'Họ tên', rồi tìm input bên trong/gần đó
            print("(!) Dùng cách dự phòng tìm ô Tên...")
            name_input = driver.find_element(By.XPATH, "//div[contains(., 'Họ tên')]//input")
            name_input.send_keys(MY_NAME)
            print(f"[OK] Đã điền tên (Dự phòng): {MY_NAME}")

        # === BƯỚC 3: ĐIỀN MÃ NV (Dựa trên video: Câu hỏi số 3) ===
        try:
            id_input = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'Mã nhân viên')]")
            id_input.send_keys(MY_ID)
            print(f"[OK] Đã điền mã: {MY_ID}")
        except:
            print("(!) Dùng cách dự phòng tìm ô Mã NV...")
            id_input = driver.find_element(By.XPATH, "//div[contains(., 'Mã nhân viên')]//input")
            id_input.send_keys(MY_ID)
            print(f"[OK] Đã điền mã (Dự phòng): {MY_ID}")

        time.sleep(1)

        # === BƯỚC 4: CHỌN BỘ PHẬN (Xquang) ===
        try:
            dept_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Xquang')]")
            driver.execute_script("arguments[0].scrollIntoView();", dept_btn) # Cuộn xuống cho thấy
            time.sleep(1)
            dept_btn.click()
            print("[OK] Đã chọn: Xquang")
        except:
             print("[ERROR] Không tìm thấy nút Xquang!")

        # === BƯỚC 5: ĐĂNG KÝ ĂN TRƯA ===
        try:
            # Tìm chính xác nút radio 'ăn trưa' (tránh nhầm với tiêu đề)
            lunch_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'ăn trưa')]")
            lunch_btn.click()
            print("[OK] Đã chọn: Ăn trưa")
        except:
            print("[ERROR] Không tìm thấy nút Ăn trưa!")

        time.sleep(2)

        # === BƯỚC CUỐI: GỬI FORM ===
        try:
            # Tìm nút có chữ Gửi
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            submit_btn.click()
            print("=> ĐÃ BẤM NÚT GỬI THÀNH CÔNG!")
        except:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            submit_btn.click()
            print("=> ĐÃ BẤM SUBMIT (Tiếng Anh)!")
        
        time.sleep(5) # Chờ hệ thống ghi nhận

    except Exception as e:
        print(f"[LỖI NGHIÊM TRỌNG]: {e}")
        # In ra cấu trúc web để debug nếu cần
        # print(driver.page_source) 
    finally:
        driver.quit()

if __name__ == "__main__":
    if check_schedule():
        book_rice()
