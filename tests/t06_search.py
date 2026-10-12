# TC06_SearchCombo.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from common_web import make_driver, search, assert_search_has_results, assert_search_no_results, W

def make_driver_keep_open():
    """Create a Chrome driver that stays open after the script finishes."""
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("detach", True)  # ✅ Keep browser window open
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    return d

if __name__ == "__main__":
    d = make_driver_keep_open()

    # 1) Valid search
    search(d, "iPhone")  # Expected to exist
    W(d, 8).until(lambda x: "search" in x.current_url.lower() or "iphone" in x.page_source.lower())
    assert_search_has_results(d)
    print("Search valid: results present")

    # 2) Invalid search (should show 'no product' message)
    search(d, "Cheers UTS!")  # Expected not to exist
    W(d, 8).until(lambda x: "search" in x.current_url.lower())
    assert_search_no_results(d)
    print("Search invalid: no results message")

    print("TC06 OK — search tests completed.")
    print("Browser window is kept open (detach=True). Close it manually when done.")
    # d.quit()  # intentionally disabled to keep browser open
