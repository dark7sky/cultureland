from selenium import webdriver
import pickle


def save_cookies(driver: webdriver.Chrome, ckf: str, dbg_msg, dbg: bool) -> bool:
    try:
        dbg_msg(dbg, "=== Saving cookies")
    except:
        print("=== Saving cookies")
    try:
        a = driver.get_cookies()
        with open(ckf, "wb") as f:
            pickle.dump(a, f)
        return True
    except:
        try:
            dbg_msg(dbg, "=> Saving cookies ==> Failed")
        except:
            print("=> Saving cookies ==> Failed")
        return False


def load_cookies(driver: webdriver.Chrome, ckf: str, dbg_msg, dbg: bool) -> bool:
    try:
        dbg_msg(dbg, "=== Loading cookies")
    except:
        print("=== Loading cookies")
    try:
        with open(ckf, "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    except:
        try:
            dbg_msg(dbg, "=> Loading cookies ==> Failed")
        except:
            print("=> Loading cookies ==> Failed")
        return False
