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
# Link Google Sheet của bạn
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'
# Link Form Test (hoặc Form thật)
LINK_FORM = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAADa9laBUQk1OMzJJTE1YVUtHOTZDNTc4N0gzOE9QUS4u'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"
# ----------------

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
                    return False
        print("-> Không thấy ngày hôm nay. Mặc định: NGHỈ.")
        return False
    except Exception as e:
        print(f"Lỗi đọc lịch: {e}")
        return False

def book_rice():
    print("--- 2. BẮT ĐẦU ĐIỀN FORM ---")
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
            print("[OK] Chọn 34 ĐCV")
        except:
            driver.execute_script("window.scrollTo(0, 200)")
            driver.find_element(By.XPATH, "//span[contains(text(), '34 ĐCV')]").click()

        time.sleep(1)

        # 2. Tên (Dùng cách dự phòng luôn cho chắc)
        try:
            driver.find_element(By.XPATH, "//div[contains(., 'Họ tên')]//input").send_keys(MY_NAME)
            print(f"[OK] Điền tên: {MY_NAME}")
        except:
            # Dự phòng cấp 2: Tìm input thứ 1
            driver.find_elements(By.TAG_NAME, "input")[0].send_keys(MY_NAME)

        # 3. Mã
        try:
            driver.find_element(By.XPATH, "//div[contains(., 'Mã nhân viên')]//input").send_keys(MY_ID)
            print(f"[OK] Điền mã: {MY_ID}")
        except:
            # Dự phòng cấp 2: Tìm input thứ 2
            driver.find_elements(By.TAG_NAME, "input")[1].send_keys(MY_ID)

        time.sleep(1)

        # 4. Xquang
        try:
            elem = driver.find_element(By.XPATH, "//span[contains(text(), 'Xquang')]")
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            elem.click()
            print("[OK] Chọn Xquang")
        except:
            print("[ERROR] Lỗi Xquang")

        # 5. Ăn trưa
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'ăn trưa')]").click()
            print("[OK] Chọn Ăn trưa")
        except:
            try:
                driver.find_element(By.XPATH, "//span[contains(text(), 'Ăn trưa')]").click() # Viết hoa
            except:
                print("[ERROR] Lỗi Ăn trưa")

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
        
        # --- QUAN TRỌNG: CHỜ XÁC NHẬN ---
        print("Đang chờ xác nhận từ Server...")
        time.sleep(15) # Chờ hẳn 15 giây cho chắc chắn
        
        # Kiểm tra xem có hiện màn hình cảm ơn không
        if "response" in driver.current_url or "ResponsePage" in driver.current_url:
             print("=> XÁC NHẬN: GỬI THÀNH CÔNG (Vẫn ở trang Response).")
        
        # Chụp thử cái tiêu đề trang web xem là gì
        print(f"Tiêu đề trang hiện tại: {driver.title}")

    except Exception as e:
        print(f"[LỖI]: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if check_schedule():
        book_rice()
