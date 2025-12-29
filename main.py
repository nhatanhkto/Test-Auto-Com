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

# ==============================================================================
# CẤU HÌNH (BẠN CHỈ CẦN SỬA LINK Ở ĐÂY LÀ DÙNG MÃI MÃI)
# ==============================================================================

# 1. Link Google Sheet (Lịch làm việc)
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'

# 2. Link Form (Đang để Link Test để bạn check nốt, check xong thay Link thật vào)
LINK_FORM = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAADa9laBUQk1OMzJJTE1YVUtHOTZDNTc4N0gzOE9QUS4u'
# Khi nào chạy thật thì xóa dòng trên, dùng dòng dưới này:
# LINK_FORM = 'https://forms.office.com/r/ZjK2MqRCUw'

MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"

# ==============================================================================

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
                    return True # Đổi thành True để chạy
                else:
                    print(f"-> Trạng thái '{status}' => NGHỈ.")
                    return False
        print("-> Không thấy ngày hôm nay. Mặc định: NGHỈ.")
        return False
    except Exception as e:
        print(f"Lỗi đọc lịch: {e}")
        return False

# HÀM MỚI: Click "Huỷ Diệt" - Click mọi ngóc ngách của phần tử
def aggressive_click(driver, text_target):
    print(f"-> Đang tìm và click mục: '{text_target}'...")
    try:
        # Tìm tất cả các thẻ chứa dòng chữ này (span, div, label...)
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text_target}')]")
        
        clicked = False
        for elem in elements:
            try:
                # 1. Cuộn đến nơi
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                time.sleep(0.5)
                
                # 2. Click bằng Javascript (Mạnh nhất)
                driver.execute_script("arguments[0].click();", elem)
                
                # 3. Click bằng Selenium (Chuẩn)
                try: elem.click() 
                except: pass

                # 4. Click vào thằng Bố nó (Phòng trường hợp chữ không click được mà phải click vào khung)
                try: 
                    parent = elem.find_element(By.XPATH, "./..")
                    driver.execute_script("arguments[0].click();", parent)
                except: pass

                clicked = True
            except:
                continue
        
        if clicked:
            print(f"   [OK] Đã thực hiện click vào '{text_target}'")
        else:
            print(f"   [WARNING] Không tìm thấy chữ '{text_target}' để click")

    except Exception as e:
        print(f"   [LỖI] Khi click '{text_target}': {e}")

# HÀM ĐIỀN CHỮ: Dùng Javascript tiêm thẳng vào ô
def force_fill_input(driver, keywords, value):
    print(f"-> Đang điền '{value}'...")
    filled = False
    
    # Cách 1: Tìm ô input có aria-label chứa từ khóa (Chính xác nhất của MS Form)
    for kw in keywords:
        try:
            inp = driver.find_element(By.XPATH, f"//input[contains(@aria-label, '{kw}')]")
            driver.execute_script("arguments[0].value = arguments[1];", inp, value)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", inp)
            filled = True
            print(f"   [OK] Đã điền vào ô có nhãn '{kw}'")
            break
        except:
            continue
            
    # Cách 2: Nếu chưa điền được, tìm mọi ô input text rồi điền theo thứ tự
    if not filled:
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            valid_inputs = [i for i in all_inputs if i.get_attribute("type") in ["text", "email", "", None] and i.is_displayed()]
            
            # Logic riêng cho Tên và Mã
            if "Họ tên" in keywords and len(valid_inputs) >= 1:
                driver.execute_script("arguments[0].value = arguments[1];", valid_inputs[0], value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", valid_inputs[0])
                print("   [OK] Đã điền theo thứ tự (Ô số 1)")
            elif "Mã" in keywords and len(valid_inputs) >= 2:
                driver.execute_script("arguments[0].value = arguments[1];", valid_inputs[1], value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", valid_inputs[1])
                print("   [OK] Đã điền theo thứ tự (Ô số 2)")
        except:
            print("   [FAIL] Không điền được dữ liệu.")

def book_rice():
    print("--- 2. BẮT ĐẦU QUY TRÌNH ---")
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
        time.sleep(8) # Chờ Web load ổn định
        print("Đã truy cập Form.")

        # 1. CHỌN 34 ĐCV
        aggressive_click(driver, "34 ĐCV")
        time.sleep(1)

        # 2. ĐIỀN HỌ TÊN
        force_fill_input(driver, ["Họ tên", "Tên"], MY_NAME)
        
        # 3. ĐIỀN MÃ NV
        force_fill_input(driver, ["Mã nhân viên", "Mã"], MY_ID)
        time.sleep(1)

        # 4. CHỌN XQUANG
        aggressive_click(driver, "Xquang")
        time.sleep(1)

        # 5. CHỌN ĂN TRƯA (MỤC TIÊU QUAN TRỌNG NHẤT)
        # Thử click mọi biến thể của chữ này
        aggressive_click(driver, "ăn trưa") 
        aggressive_click(driver, "Ăn trưa")
        time.sleep(1)

        # 6. BẤM GỬI
        print("-> Chuẩn bị bấm Gửi...")
        try:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            submit_btn.click()
            print("   [OK] Đã bấm nút Gửi")
        except:
            try:
                submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
                submit_btn.click()
                print("   [OK] Đã bấm nút Submit")
            except:
                print("   [LỖI] Không tìm thấy nút Gửi!")

        # 7. CHỤP ẢNH BẰNG CHỨNG
        print("Đang chờ kết quả 10 giây...")
        time.sleep(10)
        driver.save_screenshot("evidence.png")
        print("=> ĐÃ CHỤP ẢNH KẾT QUẢ.")

    except Exception as e:
        print(f"[LỖI HỆ THỐNG]: {e}")
        driver.save_screenshot("evidence.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Để kiểm tra lần cuối, hãy đảm bảo Google Sheet hôm nay có tích 'x'
    if check_schedule():
        book_rice()
    else:
        print("Hôm nay lịch nghỉ. Không chạy.")
