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
# CẤU HÌNH (SỬA LINK THẬT VÀO ĐÂY KHI TEST XONG)
# ==============================================================================
LINK_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdoBQimFR-crsXdoqJmC-bk5PdlR4VYVRSTVGaXncW90ogVvS8zhIjfxDRHnlB3oKHGdXcSvL5IFd/pub?gid=0&single=true&output=csv'

# LINK FORM TEST (Hiện tại dùng link này để check nốt lỗi "ăn trưa")
LINK_FORM = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAADa9laBUQk1OMzJJTE1YVUtHOTZDNTc4N0gzOE9QUS4u'
# LINK_FORM = 'https://forms.office.com/r/ZjK2MqRCUw' # <--- Link thật (bỏ dấu # ở đầu để dùng)

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
                    return True
                else:
                    print(f"-> Trạng thái '{status}' => NGHỈ.")
                    return False
        print("-> Không thấy ngày hôm nay. Mặc định: NGHỈ.")
        return False
    except Exception as e:
        print(f"Lỗi đọc lịch: {e}")
        return False

# HÀM MỚI: TIÊM DỮ LIỆU VÀO Ô TEXT (Không cần gõ phím)
def inject_text(driver, keywords, value):
    print(f"-> Đang tiêm dữ liệu '{value}'...")
    try:
        # Tìm input theo aria-label (Chuẩn nhất của MS)
        found = False
        for kw in keywords:
            try:
                inp = driver.find_element(By.XPATH, f"//input[contains(@aria-label, '{kw}')]")
                driver.execute_script("arguments[0].value = arguments[1];", inp, value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
                found = True
                print(f"   [OK] Đã tiêm vào ô '{kw}'")
                break
            except: pass
        
        # Nếu không thấy label, tìm input theo thứ tự hiển thị
        if not found:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            # Lọc input text
            text_inputs = [i for i in all_inputs if i.get_attribute("type") in ["text", "email", "", None] and i.is_displayed()]
            
            if "Tên" in keywords and len(text_inputs) >= 1:
                driver.execute_script("arguments[0].value = arguments[1];", text_inputs[0], value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", text_inputs[0])
                print("   [OK] Đã tiêm vào Input số 1 (Dự phòng)")
            elif "Mã" in keywords and len(text_inputs) >= 2:
                driver.execute_script("arguments[0].value = arguments[1];", text_inputs[1], value)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", text_inputs[1])
                print("   [OK] Đã tiêm vào Input số 2 (Dự phòng)")
                
    except Exception as e:
        print(f"   [LỖI TIÊM TEXT]: {e}")

# HÀM MỚI: HACK RADIO BUTTON (Chọn bất chấp)
def hack_radio_button(driver, keyword):
    print(f"-> Đang Hack nút: '{keyword}'...")
    try:
        # 1. Tìm tất cả các thẻ chứa chữ đó
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
        
        success = False
        for elem in elements:
            try:
                # Cuộn tới nơi
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                
                # CÁCH 1: Click thẳng vào chữ
                try: elem.click() 
                except: pass
                
                # CÁCH 2: Tìm nút radio (input) nằm gần cái chữ đó nhất và ép CHECKED
                # Tìm ngược lên cha, rồi tìm input radio con của cha
                try:
                    parent = elem.find_element(By.XPATH, "./..") # Lên 1 cấp
                    grandparent = elem.find_element(By.XPATH, "./../..") # Lên 2 cấp
                    
                    # Tìm input radio trong khu vực lân cận
                    radios = grandparent.find_elements(By.TAG_NAME, "input")
                    for radio in radios:
                        if radio.get_attribute("type") == "radio":
                            driver.execute_script("arguments[0].click();", radio) # Click JS
                            success = True
                except: pass

                # CÁCH 3: Click vào mọi thẻ div/span bao quanh nó
                driver.execute_script("arguments[0].click();", elem)
                success = True
            except: continue
            
        if success:
            print(f"   [OK] Đã kích hoạt vùng chọn '{keyword}'")
        else:
            print(f"   [WARN] Không tìm thấy vùng chọn '{keyword}'")

    except Exception as e:
        print(f"   [LỖI HACK RADIO]: {e}")

def book_rice():
    print("--- 2. BẮT ĐẦU (CHẾ ĐỘ DOM HACKING) ---")
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
        print("Đã vào Form.")

        # 1. CHỌN 34 ĐCV
        hack_radio_button(driver, "34 ĐCV")
        time.sleep(1)

        # 2. TIÊM TÊN (Không gõ phím nữa, tiêm thẳng)
        inject_text(driver, ["Họ tên", "Tên"], MY_NAME)
        
        # 3. TIÊM MÃ
        inject_text(driver, ["Mã nhân viên", "Mã"], MY_ID)
        time.sleep(1)

        # 4. CHỌN KHOA
        hack_radio_button(driver, "Xquang")
        
        # 5. CHỌN ĂN TRƯA (QUAN TRỌNG NHẤT)
        # Thử nhiều từ khoá khác nhau để chắc ăn
        hack_radio_button(driver, "ăn trưa") 
        hack_radio_button(driver, "Ăn trưa")
        
        # KỸ THUẬT CUỐI: Tìm input radio cuối cùng trên trang (thường là nó) và click
        try:
             all_radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
             # Lấy các radio có value chứa chữ "trưa" hoặc label chứa chữ "trưa"
             # Nhưng đơn giản nhất: click vào div chứa chữ "ăn trưa"
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
        print("=> ĐÃ CHỤP ẢNH MÀN HÌNH")

    except Exception as e:
        print(f"[LỖI]: {e}")
        driver.save_screenshot("evidence.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test luôn không cần check lịch lúc này
    book_rice()
