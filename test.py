import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://54.177.41.132:5000"

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def accept_alert_if_present(driver, timeout=5):
    try:
        alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert.accept()
    except TimeoutException:
        pass


def test_index_page_loads(driver):
    driver.get(f"{BASE_URL}/")
    assert "Product Order App" in driver.title


def test_navigation_to_login(driver):
    driver.get(f"{BASE_URL}/")
    driver.find_element(By.LINK_TEXT, "Login").click()
    assert driver.current_url.endswith("/login.html")


def test_navigation_to_signup(driver):
    driver.get(f"{BASE_URL}/")
    driver.find_element(By.LINK_TEXT, "Signup").click()
    assert driver.current_url.endswith("/signup.html")


def test_signup_duplicate_user(driver):
    driver.get(f"{BASE_URL}/signup.html")
    driver.find_element(By.ID, "username").send_keys("shahwaiz1")
    driver.find_element(By.ID, "password").send_keys("anything123")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    # handle alert
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    text = alert.text.lower()
    assert "exists" in text or "failed" in text
    alert.accept()


def test_login_success(driver):
    driver.get(f"{BASE_URL}/login.html")
    driver.find_element(By.ID, "username").send_keys("shahwaiz1")
    driver.find_element(By.ID, "password").send_keys("123")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    # accept "Login successful!" alert
    accept_alert_if_present(driver)
    # then wait for redirect
    WebDriverWait(driver, 5).until(EC.url_contains("products.html"))
    assert "products.html" in driver.current_url


def test_login_invalid_credentials(driver):
    driver.get(f"{BASE_URL}/login.html")
    driver.find_element(By.ID, "username").send_keys("no_such_user")
    driver.find_element(By.ID, "password").send_keys("wrongpass")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    # should get "Invalid credentials." alert
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    text = alert.text.lower()
    assert "invalid credentials" in text
    alert.accept()


def test_products_page_loads(driver):
    # ensure no stale alert
    accept_alert_if_present(driver)
    driver.get(f"{BASE_URL}/products.html")
    cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card"))
    )
    assert len(cards) > 0


def test_add_to_cart_and_display(driver):
    driver.get(f"{BASE_URL}/products.html")
    btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart"))
    )
    btn.click()
    # accept "Added ... to cart!" alert
    accept_alert_if_present(driver)
    driver.get(f"{BASE_URL}/cart.html")
    items = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cart-item"))
    )
    assert len(items) >= 1


def test_remove_item_from_cart(driver):
    driver.get(f"{BASE_URL}/cart.html")
    remove_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".remove-item"))
    )
    remove_btn.click()
    time.sleep(1)
    items = driver.find_elements(By.CSS_SELECTOR, ".cart-item")
    empty_msg = driver.find_elements(By.CSS_SELECTOR, "#cartContainer p")
    assert len(items) == 0 or any("empty" in e.text.lower() for e in empty_msg)


def test_place_order_clears_cart(driver):
    driver.get(f"{BASE_URL}/cart.html")
    if not driver.find_elements(By.CSS_SELECTOR, ".cart-item"):
        driver.get(f"{BASE_URL}/products.html")
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart"))
        ).click()
        accept_alert_if_present(driver)
        driver.get(f"{BASE_URL}/cart.html")
    driver.find_element(By.ID, "placeOrderBtn").click()
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    assert "success" in alert.text.lower()
    alert.accept()
    driver.get(f"{BASE_URL}/cart.html")
    empty_msg = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cartContainer p"))
    )
    assert "empty" in empty_msg.text.lower()
