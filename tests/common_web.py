# common_web.py
import time, random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException


HOME = "https://ecommerce-playground.lambdatest.io/"
REGISTER = HOME + "index.php?route=account/register"
LOGIN = HOME + "index.php?route=account/login"
CART = HOME + "index.php?route=checkout/cart"

def make_driver(w=1360, h=900):
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("detach", False)
    svc = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=svc, options=opts)
    d.set_window_size(w, h)
    return d

def W(d, t=10): return WebDriverWait(d, t)

def click(d, el):
    try: el.click()
    except ElementClickInterceptedException:
        d.execute_script("arguments[0].click()", el)

def scroll_into(d, el): d.execute_script("arguments[0].scrollIntoView({block:'center'})", el)

def ss(d, out_dir: Path, name: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{name}.png"
    d.save_screenshot(str(p))
    print("[Saved]", p)

def find_first(d, selectors):
    for by, val in selectors:
        try: return d.find_element(by, val)
        except NoSuchElementException: pass
    raise NoSuchElementException(selectors)

def random_email(prefix="adella"): return f"{prefix}{random.randint(1000,9999)}@test.com"

def ensure_account(d):
    """Create one test account and return (email, pwd)."""
    email, pwd = random_email("adella"), "Test1234!"
    d.get(REGISTER)
    W(d).until(EC.visibility_of_element_located((By.ID, "input-firstname")))
    d.find_element(By.ID, "input-firstname").send_keys("Adella")
    d.find_element(By.ID, "input-lastname").send_keys("Koo")
    d.find_element(By.ID, "input-email").send_keys(email)
    d.find_element(By.ID, "input-telephone").send_keys("+61 412345678")
    d.find_element(By.ID, "input-password").send_keys(pwd)
    d.find_element(By.ID, "input-confirm").send_keys(pwd)
    agree = d.find_element(By.NAME, "agree"); scroll_into(d, agree); click(d, agree)
    btn = find_first(d, [
        (By.CSS_SELECTOR, "input[value='Continue']"),
        (By.XPATH, "//input[@type='submit' and @value='Continue']"),
        (By.XPATH, "//button[contains(.,'Continue')]"),
    ])
    scroll_into(d, btn); click(d, btn)
    W(d, 10).until(lambda x: "success" in x.current_url.lower() or "Account Has Been Created" in x.page_source)
    return email, pwd

def logout_if_possible(d):
    """Attempt to log out if a logout link is available (best-effort)."""
    try:
        d.get(HOME); time.sleep(0.3)
        links = d.find_elements(By.XPATH, "//a[contains(.,'Logout') or contains(@href,'logout')]")
        if links: click(d, links[0]); time.sleep(0.3)
    except Exception: pass

def search_open_first_product(d, keyword="iPhone"):
    """Search from the header and open the first product detail page."""
    d.get(HOME)
    sbox = find_first(d, [
        (By.NAME, "search"),
        (By.CSS_SELECTOR, "input[id*='search']"),
        (By.XPATH, "//input[@type='text' and (contains(@name,'search') or contains(@id,'search'))]"),
    ])
    sbox.clear(); sbox.send_keys(keyword); sbox.submit()
    item = W(d).until(EC.element_to_be_clickable((
        By.XPATH, "(//a[contains(@href,'product') and (contains(@class,'image') or contains(@class,'title') or contains(@class,'name'))])[1]"
    )))
    click(d, item)
    W(d).until(EC.presence_of_element_located((By.XPATH, "//h1 | //*[@id='content']//h1")))

def add_current_to_cart(d):
    """On a product detail page, click 'Add to Cart'."""
    add_btn = find_first(d, [
        (By.ID, "button-cart"),
        (By.XPATH, "//button[contains(.,'Add to Cart')]"),
        (By.CSS_SELECTOR, "button[onclick*='cart.add'], button[title*='Add to Cart']"),
    ])
    scroll_into(d, add_btn); click(d, add_btn); time.sleep(1.0)

def go_cart(d):
    """Directly open the Cart page and wait until it becomes visible."""
    d.get(CART)
    W(d).until(EC.visibility_of_element_located((By.ID, "content")))
    time.sleep(0.3)

def go_to_cart(d, wait_seconds=10):
    """Navigate to the Cart via UI (cart icon → 'View Cart'), then ensure we're on the cart page."""
    try:
        cart_icon = None
        for by, sel in [
            (By.CSS_SELECTOR, "a[title='Shopping Cart']"),
            (By.CSS_SELECTOR, "a[href*='route=checkout/cart']"),
            (By.XPATH, "//a[contains(.,'Cart') or contains(@title,'Cart')]"),
            (By.CSS_SELECTOR, "div#cart > button, #cart > button"),
        ]:
            try:
                cart_icon = d.find_element(by, sel); break
            except NoSuchElementException:
                continue
        if cart_icon:
            d.execute_script("arguments[0].scrollIntoView({block:'center'})", cart_icon)
            cart_icon.click()
            # Click the 'View Cart' button if present
            try:
                view = d.find_element(By.XPATH, "//a[contains(.,'View Cart')]")
                view.click()
            except Exception:
                pass
    except Exception:
        pass

    if "route=checkout/cart" not in d.current_url:
        d.get(CART)

    WebDriverWait(d, wait_seconds).until(
        EC.visibility_of_element_located((By.ID, "content"))
    )

# ======== EXTRA HELPERS (append) ========

def open_listing_any(d):
    """Open the home/listing and wait until the first 'Add to Cart' button is present."""
    d.get(HOME)
    W(d, 12).until(EC.presence_of_element_located((
        By.XPATH,
        "(//button[contains(@data-original-title,'Add to Cart')]"
        " | //button[contains(.,'Add to Cart')]"
        " | //button[contains(@onclick,'cart.add')])[1]"
    )))

def click_first_add_to_cart_on_listing(d):
    """From a listing (home/category), click the first 'Add to Cart' button."""
    btn = find_first(d, [
        (By.XPATH, "(//button[contains(@data-original-title,'Add to Cart')])[1]"),
        (By.XPATH, "(//button[contains(.,'Add to Cart')])[1]"),
        (By.XPATH, "(//button[contains(@onclick,'cart.add')])[1]"),
        (By.CSS_SELECTOR, "button[title*='Add to Cart']"),
    ])
    click(d, btn)

def wait_add_success(d, timeout=6):
    """Wait for an add-to-cart success signal (success alert / mini-cart badge / fallback text)."""
    try:
        alert = W(d, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))
        return ("alert", alert.text.strip())
    except TimeoutException:
        pass
    try:
        badge = d.find_element(By.CSS_SELECTOR, ".cart-qty, .cart-badge, #cart-total")
        txt = badge.text.strip()
        if any(ch.isdigit() for ch in txt):
            return ("badge", txt)
    except NoSuchElementException:
        pass
    if "added" in d.page_source.lower():
        return ("text", "added")
    raise TimeoutException("Add-to-cart success signal not found")

def cart_row_count(d):
    """Return the number of product rows in the cart table."""
    rows = d.find_elements(By.XPATH, "//table//tbody//tr")
    return len(rows)

def cart_update_quantity(d, new_qty="2"):
    """Update the first product's quantity in the cart and click 'Update'."""
    qty = find_first(d, [
        (By.CSS_SELECTOR, "input[name^='quantity']"),
        (By.XPATH, "//input[contains(@name,'quantity')]"),
    ])
    qty.clear(); qty.send_keys(new_qty)
    update_btn = find_first(d, [
        (By.XPATH, "//button[contains(@data-original-title,'Update')]"),
        (By.XPATH, "//button[contains(.,'Update')]"),
        (By.CSS_SELECTOR, "button[title*='Update']"),
    ])
    click(d, update_btn)
    time.sleep(1.0)  # short wait for the change to apply
    return qty

def cart_remove_first(d):
    """Remove the first product from the cart."""
    rm_btn = find_first(d, [
        (By.XPATH, "//button[contains(@data-original-title,'Remove')]"),
        (By.XPATH, "//button[contains(.,'Remove')]"),
        (By.CSS_SELECTOR, "button[title*='Remove'], .btn-danger[onclick*='cart.remove']"),
    ])
    click(d, rm_btn)
    time.sleep(1.0)

def search(d, keyword):
    """Execute a search from the top search box."""
    d.get(HOME)
    sbox = find_first(d, [
        (By.NAME, "search"),
        (By.CSS_SELECTOR, "input[id*='search']"),
        (By.XPATH, "//input[@type='text' and (contains(@name,'search') or contains(@id,'search'))]"),
    ])
    sbox.clear(); sbox.send_keys(keyword); sbox.submit()

def assert_search_has_results(d):
    """There must be at least one result (match any product card/link)."""
    W(d, 8).until(EC.presence_of_element_located((
        By.XPATH, "(//a[contains(@href,'product')])[1]"
    )))

def assert_search_no_results(d):
    """Wait until a 'no results' message (or equivalent text) appears."""
    W(d, 5).until(lambda x: ("no product" in x.page_source.lower()) or
                           ("no results" in x.page_source.lower()) or
                           ("no product that matches" in x.page_source.lower()))
