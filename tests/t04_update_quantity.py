# TC04_UpdateQuantity.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from common_web import open_listing_any, click_first_add_to_cart_on_listing
from common_web import wait_add_success, go_to_cart, cart_update_quantity

def make_driver_keep_open():
    """Create a Chrome driver that stays open after the script finishes."""
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("detach", True)  # Keep browser window open
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    return d

if __name__ == "__main__":
    d = make_driver_keep_open()

    # 1) Open product listing and add the first item to the cart
    open_listing_any(d)
    click_first_add_to_cart_on_listing(d)
    wait_add_success(d)

    # 2) Go to the cart
    go_to_cart(d)

    # 3) Update quantity to 333
    cart_update_quantity(d, new_qty="333")

    print(" TC04 OK — quantity updated successfully.")
    print("Browser window is kept open (detach=True). Close it manually when done.")
    # d.quit()  # intentionally disabled to keep browser open
