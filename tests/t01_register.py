# TC01_Register.py
# pip install selenium webdriver-manager

import time, random
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=account/register"

ERROR_SELECTORS = [".alert-danger", ".text-danger"]
SUCCESS_HINTS = ["your account has been created", "account has been created", "success"]

# ----------------------------------------------------------------------
# Common utilities
# ----------------------------------------------------------------------
def make_driver():
    opts = webdriver.ChromeOptions()
    # Keep window open: prevent browser from closing even after script/quit ends
    opts.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    return d

def js_scroll(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

def safe_click(driver, el):
    try:
        el.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", el)

def open_register(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#content h1"))
    )

def rand_email():
    return f"adella{random.randint(1000,9999)}@test.com"

def fill_form(driver, first="Adella", last="Koo", email=None, tel="+61 412345678",
              pwd="Test1234!", confirm="Test1234!", agree=False, omit=()):
    if email is None:
        email = rand_email()
    fields = {
        "input-firstname": None if "first" in omit else first,
        "input-lastname": None if "last" in omit else last,
        "input-email": None if "email" in omit else email,
        "input-telephone": None if "tel" in omit else tel,
        "input-password": None if "pwd" in omit else pwd,
        "input-confirm": None if "confirm" in omit else confirm,
    }
    for fid, val in fields.items():
        el = driver.find_element(By.ID, fid)
        el.clear()
        if val:
            el.send_keys(val)

    agree_box = driver.find_element(By.NAME, "agree")
    js_scroll(driver, agree_box)
    if agree and not agree_box.is_selected():
        safe_click(driver, agree_box)
    elif (not agree) and agree_box.is_selected():
        safe_click(driver, agree_box)

def page_has_success(driver):
    src = driver.page_source.lower()
    return any(k in src for k in SUCCESS_HINTS) or "route=account/success" in driver.current_url

def click_and_wait(driver, timeout=5):
    """After clicking Continue, poll briefly for success/error.
    Returns: ('success'|'error'|'timeout', [error_texts])"""
    btn = driver.find_element(By.CSS_SELECTOR, "input[value='Continue']")
    js_scroll(driver, btn)
    safe_click(driver, btn)

    end = time.time() + timeout
    while time.time() < end:
        if page_has_success(driver):
            return ("success", [])
        errs = []
        for sel in ERROR_SELECTORS:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed():
                    txt = (el.text or "").strip()
                    if txt:
                        errs.append(txt)
        if errs:
            return ("error", errs)
        time.sleep(0.1)
    return ("timeout", [])

def assert_any_contains(errs, keywords, context=""):
    joined = " | ".join(errs).lower()
    assert any(k.lower() in joined for k in keywords), f"[{context}] No match in: {errs}"

# ----------------------------------------------------------------------
# Runner (soft assertions)
# ----------------------------------------------------------------------
@dataclass
class CaseResult:
    name: str
    status: str
    msg: str = ""

results = []

def run_case(name, func):
    print(f"\n=== {name} ===")
    try:
        func()
        results.append(CaseResult(name, "PASS"))
    except AssertionError as e:
        results.append(CaseResult(name, "FAIL", str(e)))
    except Exception as e:
        results.append(CaseResult(name, "ERROR", str(e)))
    print(f"{name} → {results[-1].status}")

def summary():
    print("\n===== SUMMARY =====")
    for r in results:
        print(f"{r.name}: {r.status} {r.msg}")
    print("===================\n")

# ----------------------------------------------------------------------
# Test cases (no screenshots; console logs only)
# ----------------------------------------------------------------------
def case1_missing_fields():
    open_register(d)
    fill_form(d, agree=True, omit=("first", "email"))
    outcome, errs = click_and_wait(d)
    print("[CASE1] outcome:", outcome, "| errors:", errs)
    assert outcome == "error", f"[CASE1] Expected error, got {outcome}"
    assert_any_contains(errs, ["required", "must"], "CASE1")

def case2_pwd_mismatch():
    open_register(d)
    fill_form(d, email=rand_email(), confirm="Wrong999!", agree=True)
    outcome, errs = click_and_wait(d)
    print("[CASE2] outcome:", outcome, "| errors:", errs)
    assert outcome == "error", f"[CASE2] Expected error, got {outcome}"
    assert_any_contains(errs, ["password", "confirm"], "CASE2")

def case3_privacy_unchecked():
    open_register(d)
    fill_form(d, email=rand_email(), agree=False)
    outcome, errs = click_and_wait(d)
    print("[CASE3] outcome:", outcome, "| errors:", errs)
    assert outcome == "error", f"[CASE3] Expected error, got {outcome}"
    assert_any_contains(errs, ["privacy"], "CASE3")

def case4_valid_registration():
    open_register(d)
    fill_form(d, email=rand_email(), agree=True)
    outcome, errs = click_and_wait(d)
    print("[CASE4] outcome:", outcome, "| url:", d.current_url)
    assert outcome == "success", f"[CASE4] Expected success, got {outcome}"

# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    d = make_driver()

    run_case("TC01 - Missing Fields", case1_missing_fields)
    run_case("TC02 - Password Mismatch", case2_pwd_mismatch)
    run_case("TC03 - Privacy Unchecked", case3_privacy_unchecked)
    run_case("TC04 - Valid Registration", case4_valid_registration)

    summary()
    print("Test completed — browser window is kept open (detach=True).")
    print("Close the browser manually when you're done.")
    # driver.quit()  # intentionally disabled to keep window open
