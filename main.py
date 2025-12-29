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

# --- CẤU HÌNH (ĐÃ CẬP NHẬT CHUẨN) ---
# Link lịch trình của bạn
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'
# Link Form Test mới nhất
LINK_FORM = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAADa9laBUQk1OMzJJTE1YVUtHOTZDNTc4N0gzOE9QUS4u'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"
# ------------------------------------

def get_vietnam_time():
    # Chuyển giờ Server (UTC) sang giờ Việt Nam (UTC+7)
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
    print("--- 2. BẮT ĐẦU ĐIỀN FORM TEST ---")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        driver.get(LINK_FORM)
        # Chờ web load (tìm chữ 'Nơi làm việc' hoặc body)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        print("Đã truy cập Form thành công.")

        # === CÂU 1: CHỌN NƠI LÀM VIỆC (34 ĐCV) ===
        try:
            # Tìm thẻ span chứa chữ 34 ĐCV
            place_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '34 ĐCV')]")))
            place_btn.click()
            print("[OK] Đã chọn: 34 ĐCV")
        except:
            print("[!] Không thấy 34 ĐCV, thử cuộn trang...")
            driver.execute_script("window.scrollTo(0, 200)")
            time.sleep(1)
            driver.find_element(By.XPATH, "//span[contains(text(), '34 ĐCV')]").click()

        time.sleep(1)

        # === CÂU 2: ĐIỀN HỌ TÊN ===
        # Tìm ô input thuộc về câu hỏi có chứa chữ 'Họ tên'
        try:
            # Cách chính xác nhất: Tìm input có nhãn dán là Họ tên
            name_input = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'Họ tên')]")
            name_input.send_keys(MY_NAME)
            print(f"[OK] Đã điền tên: {MY_NAME}")
        except:
            # Cách dự phòng: Tìm khối chứa chữ Họ tên rồi tìm input bên trong
            print("(!) Dùng cách tìm dự phòng cho Tên...")
            name_input = driver.find_element(By.XPATH, "//div[contains(., 'Họ tên')]//input")
            name_input.send_keys(MY_NAME)
            print(f"[OK] Đã điền tên (Dự phòng): {MY_NAME}")

        # === CÂU 3: ĐIỀN MÃ NHÂN VIÊN ===
        try:
            id_input = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'Mã nhân viên')]")
            id_input.send_keys(MY_ID)
            print(f"[OK] Đã điền mã: {MY_ID}")
        except:
            print("(!) Dùng cách tìm dự phòng cho Mã NV...")
            id_input = driver.find_element(By.XPATH, "//div[contains(., 'Mã nhân viên')]//input")
            id_input.send_keys(MY_ID)
            print(f"[OK] Đã điền mã (Dự phòng): {MY_ID}")

        time.sleep(1)

        # === CÂU 4: CHỌN BỘ PHẬN (Xquang) ===
        try:
            dept_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Xquang')]")
            driver.execute_script("arguments[0].scrollIntoView();", dept_btn)
            time.sleep(1)
            dept_btn.click()
            print("[OK] Đã chọn: Xquang")
        except:
            print("[ERROR] Lỗi chọn Xquang")

        # === CÂU 5: ĐĂNG KÝ ĂN TRƯA ===
        try:
            lunch_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'ăn trưa')]")
            lunch_btn.click()
            print("[OK] Đã chọn: Ăn trưa")
        except:
            # Thử tìm chữ viết hoa Ăn trưa
            try:
                lunch_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Ăn trưa')]")
                lunch_btn.click()
                print("[OK] Đã chọn: Ăn trưa (Viết hoa)")
            except:
                print("[ERROR] Lỗi chọn Ăn trưa")

        time.sleep(1)

        # === GỬI ===
        try:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            submit_btn.click()
            print("=> ĐÃ BẤM GỬI THÀNH CÔNG!")
        except:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            submit_btn.click()
            print("=> ĐÃ BẤM SUBMIT!")
        
        time.sleep(3)

    except Exception as e:
        print(f"[LỖI RỒI]: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if check_schedule():
        book_rice()
