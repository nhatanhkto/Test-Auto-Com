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
# CẤU HÌNH CHÍNH THỨC
# ==============================================================================

# 1. Link Google Sheet
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'

# 2. Link Form THẬT
LINK_FORM = 'https://forms.office.com/r/ZjK2MqRCUw'

# 3. Thông tin cá nhân
MY_NAME = "Vũ Thị Thơm"
MY_ID = "BVHV00491"

# ==============================================================================

def get_vietnam_time():
    utc_now = datetime.now(timezone.utc)
    vn_now = utc_now + timedelta(hours=7)
    return vn_now

# HÀM MỚI: CHUẨN HÓA NGÀY THÁNG ĐỂ SO SÁNH (6/1 sẽ bằng 06/01)
def normalize_date(date_str):
    try:
        # Xóa khoảng trắng thừa
        date_str = date_str.strip()
        # Tách ngày, tháng, năm dựa trên dấu gạch chéo
        parts = date_str.split('/')
        if len(parts) == 3:
            day = int(parts[0])   # Chuyển "06" thành số 6
            month = int(parts[1]) # Chuyển "01" thành số 1
            year = int(parts[2])  # 2026
            # Trả về chuỗi chuẩn dạng số: "6/1/2026"
            return f"{day}/{month}/{year}"
        return date_str
    except:
        return date_str

def check_schedule():
    print("--- 1. KIỂM TRA LỊCH TRÌNH (CHO NGÀY MAI) ---")
    try:
        response = requests.get(LINK_CSV)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
        
        # Lấy giờ VN hiện tại
        vn_now = get_vietnam_time()
        
        # TÍNH NGÀY MAI
        tomorrow_vn = vn_now + timedelta(days=1)
        
        # Tạo ra 2 định dạng để tìm kiếm cho chắc ăn
        tomorrow_str_full = tomorrow_vn.strftime("%d/%m/%Y") # Dạng 06/01/2026
        tomorrow_str_short = f"{tomorrow_vn.day}/{tomorrow_vn.month}/{tomorrow_vn.year}" # Dạng 6/1/2026
        
        print(f"Hôm nay là: {vn_now.strftime('%d/%m/%Y')}")
        print(f"-> Đang tìm lịch cho NGÀY MAI ({tomorrow_str_full} hoặc {tomorrow_str_short})...")
        
        reader = csv.DictReader(lines)
        found_date = False
        
        for row in reader:
            csv_date_raw = row['Ngay']
            # Chuẩn hóa cả 2 bên về dạng số để so sánh (6 == 06)
            norm_csv_date = normalize_date(csv_date_raw)
            norm_target_date = normalize_date(tomorrow_str_full)
            
            if norm_csv_date == norm_target_date:
                found_date = True
                status = row['DiLam'].lower().strip()
                print(f"   [TÌM THẤY] Dòng trong Excel: '{csv_date_raw}' - Trạng thái: '{status}'")
                
                if status == 'x' or status == 'co' or status == 'có':
                    print(f"=> KẾT LUẬN: Ngày mai CÓ LÀM. Tiến hành Đăng ký ngay.")
                    return True
                else:
                    print(f"=> KẾT LUẬN: Ngày mai NGHỈ. Không đăng ký.")
                    return False
                    
        if not found_date:
            print(f"-> LỖI: Đã duyệt hết file Excel mà không thấy ngày {tomorrow_str_full}.")
            print("   (Hãy kiểm tra lại file Google Sheet xem đã điền ngày mai chưa?)")
            
        return False

    except Exception as e:
        print(f"Lỗi đọc lịch: {e}")
        return False

# HÀM: TIÊM DỮ LIỆU
def inject_text(driver, keywords, value):
    print(f"-> Đang điền '{value}'...")
    try:
        found = False
        for kw in keywords:
            try:
                inp = driver.find_element(By.XPATH, f"//input[contains(@aria-label, '{kw}')]")
                driver.execute_script("arguments[0].value = arguments[1];", inp, value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
                found = True
                print(f"   [OK] Đã điền vào ô '{kw}'")
                break
            except: pass
        
        if not found:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            text_inputs = [i for i in all_inputs if i.get_attribute("type") in ["text", "email", "", None] and i.is_displayed()]
            
            if "Tên" in keywords and len(text_inputs) >= 1:
                driver.execute_script("arguments[0].value = arguments[1];", text_inputs[0], value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", text_inputs[0])
            elif "Mã" in keywords and len(text_inputs) >= 2:
                driver.execute_script("arguments[0].value = arguments[1];", text_inputs[1], value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", text_inputs[1])

    except Exception as e:
        print(f"   [LỖI ĐIỀN TEXT]: {e}")

# HÀM: HACK RADIO BUTTON
def hack_radio_button(driver, keyword):
    print(f"-> Đang chọn: '{keyword}'...")
    try:
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
        for elem in elements:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                driver.execute_script("arguments[0].click();", elem)
                try:
                    parent = elem.find_element(By.XPATH, "./..")
                    grandparent = elem.find_element(By.XPATH, "./../..")
                    radios = grandparent.find_elements(By.TAG_NAME, "input")
                    for radio in radios:
                        if radio.get_attribute("type") == "radio":
                            driver.execute_script("arguments[0].click();", radio)
                except: pass
            except: continue
    except Exception as e:
        print(f"   [LỖI RADIO]: {e}")

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
        time.sleep(8)
        print("Đã vào Form Công Ty.")

        # 1. CHỌN 34 ĐCV
        hack_radio_button(driver, "34 ĐCV")
        time.sleep(1)

        # 2. ĐIỀN TÊN
        inject_text(driver, ["Họ tên", "Tên"], MY_NAME)
        
        # 3. ĐIỀN MÃ
        inject_text(driver, ["Mã nhân viên", "Mã"], MY_ID)
        time.sleep(1)

        # 4. CHỌN XQUANG
        hack_radio_button(driver, "Xquang")
        
        # 5. CHỌN ĂN TRƯA
        hack_radio_button(driver, "ăn trưa") 
        hack_radio_button(driver, "Ăn trưa")
        
        try:
             target = driver.find_element(By.XPATH, "//div[contains(., 'ăn trưa')]")
             driver.execute_script("arguments[0].click();", target)
        except: pass

        time.sleep(2)

        # 6. GỬI
        print("Chuẩn bị Gửi...")
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Gửi')]")
            btn.click()
            print("   [OK] Đã bấm Gửi")
        except:
            btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            btn.click()
            print("   [OK] Đã bấm Submit")
        
        print("Đang chờ kết quả 15 giây...")
        time.sleep(15)
        
        driver.save_screenshot("evidence.png")
        print("=> ĐÃ CHỤP ẢNH KẾT QUẢ.")

    except Exception as e:
        print(f"[LỖI]: {e}")
        driver.save_screenshot("evidence.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    if check_schedule():
        book_rice()
    else:
        print("Kết thúc quy trình (Do ngày mai nghỉ hoặc không tìm thấy lịch).")
