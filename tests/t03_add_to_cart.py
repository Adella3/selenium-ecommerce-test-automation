# TC03_AddToCart.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from common_web import HOME, go_cart, W, find_first, click

def make_driver_keep_open():
    """Create a Chrome driver that stays open even after the script ends."""
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("detach", True)  # ✅ keep browser window open
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    return d

def open_listing_any(d):
    """Open the homepage (or default product listing) and wait until product cards are visible."""
    d.get(HOME)
    # Wait for any product card/button to appear
    W(d, 12).until(EC.presence_of_element_located((
        By.XPATH,
        "(//button[contains(@data-original-title,'Add to Cart')]"
        " | //button[contains(.,'Add to Cart')]"
        " | //button[contains(@onclick,'cart.add')])[1]"
    )))

def click_first_add_to_cart(d):
    """Click the first visible 'Add to Cart' button."""
    btn = find_first(d, [
        (By.XPATH, "(//button[contains(@data-original-title,'Add to Cart')])[1]"),
        (By.XPATH, "(//button[contains(.,'Add to Cart')])[1]"),
        (By.XPATH, "(//button[contains(@onclick,'cart.add')])[1]"),
        (By.CSS_SELECTOR, "button[title*='Add to Cart']"),
    ])
    click(d, btn)

def wait_add_success(d):
    """Wait for an add-to-cart success signal (alert/toast/badge change)."""
    # 1) Green success alert
    try:
        alert = W(d, 6).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))
        return ("alert", alert.text.strip())
    except TimeoutException:
        pass
    # 2) Mini-cart badge update
    try:
        badge = d.find_element(By.CSS_SELECTOR, ".cart-qty, .cart-badge, #cart-total")
        txt = badge.text.strip()
        if any(ch.isdigit() for ch in txt):
            return ("badge", txt)
    except NoSuchElementException:
        pass
    # 3) Fallback: “added” text in page source
    if "added" in d.page_source.lower():
        return ("text", "added")
    raise TimeoutException("Add-to-cart success signal not found")

if __name__ == "__main__":
    d = make_driver_keep_open()

    # 1) Open listing
    open_listing_any(d)

    # 2) Add the first product to the cart
    click_first_add_to_cart(d)
    kind, info = wait_add_success(d)
    print(f"[AddToCart] success via {kind}: {info}")

    # 3) Go to the Cart page and verify
    go_cart(d)

    rows = d.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) >= 1, "Cart appears empty (no table rows)"

    print("TC03 OK — item successfully added to cart.")
    print("Browser window is kept open (detach=True). Close it manually when done.")
    # d.quit()  # intentionally disabled to keep browser open
