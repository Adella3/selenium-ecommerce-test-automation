# TC02_Login.py
# pip install selenium webdriver-manager

from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common_web import (
    make_driver, ensure_account, logout_if_possible, W, LOGIN,
    find_first, scroll_into, click
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def make_driver_keep_open():
    """Create a Chrome driver that stays open even after the script ends."""
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("detach", True)  # keep browser window open
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    return d


def wait_for_invalid(d, timeout=10):
    """Wait until a login alert (.alert-danger) appears."""
    def _cond(x):
        try:
            a = x.find_element(By.CSS_SELECTOR, ".alert-danger")
            return a if a.is_displayed() else False
        except NoSuchElementException:
            return False
    return W(d, timeout).until(_cond)


def wait_for_account(d, timeout=12):
    """Wait until the account page is loaded (by URL or 'My Account' text)."""
    return W(d, timeout).until(
        lambda x: ("account/account" in x.current_url.lower()) or ("my account" in x.page_source.lower())
    )


def do_login_once(d, email, pwd, tag):
    """tag: 'invalid' | 'valid'"""
    d.get(LOGIN)
    W(d).until(EC.visibility_of_element_located((By.ID, "input-email")))
    email_el = d.find_element(By.ID, "input-email")
    pwd_el = d.find_element(By.ID, "input-password")
    email_el.clear(); email_el.send_keys(email)
    pwd_el.clear();   pwd_el.send_keys(pwd)

    btn = find_first(d, [
        (By.XPATH, "//input[@type='submit' and @value='Login']"),
        (By.XPATH, "//button[contains(.,'Login')]"),
    ])
    scroll_into(d, btn); click(d, btn)

    # Wait for result
    try:
        if tag == "invalid":
            alert_el = wait_for_invalid(d, timeout=10)
            print("[INVALID] Alert text:", alert_el.text.strip())
        else:
            wait_for_account(d, timeout=12)
    except TimeoutException:
        print(f"[TIMEOUT] Login did not finish for tag={tag}")
        raise


if __name__ == "__main__":
    # 0) Launch browser (window persistence handled by make_driver_keep_open)
    d = make_driver_keep_open()

    # 1) Create a temporary test account
    email, pwd = ensure_account(d)

    # 2) Reset state: logout + clear cookies (avoid already-logged-in state)
    logout_if_possible(d)
    d.delete_all_cookies()

    # 3) Invalid password scenario
    do_login_once(d, email, "Wrong999!", "invalid")

    # 4) Valid credentials scenario (clear cookies again)
    d.delete_all_cookies()
    do_login_once(d, email, pwd, "valid")

    print("TC02 complete — browser window is kept open (detach=True).")
    print("Close the browser manually when finished.")
    # d.quit()  # intentionally disabled to keep browser open
