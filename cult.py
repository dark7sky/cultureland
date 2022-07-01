from typing import KeysView
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import telegram
import time
import cookies
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import datetime

## python -m PyInstaller -F Check_currency.py --collect-data selenium --collect-data certifi
config_data = {
    "login_url": "https://m.cultureland.co.kr/csh/cshGiftCard.do",
    "pic_capcha": "capcha.png",
    "xpaths": {
        "ID": '//*[@id="txtUserId"]',
        "PSSWD": '//*[@id="passwd"]',
        "KEYPAD": '//img[@alt="',
        "KEYPAD_done": '//img[@alt="입력완료"]',
        "capcha": '//*[@id="captchaCode"]',
        "checkBox_ID": '//*[@id="frmLogin"]/fieldset/p/label[1]',
        "checkBox_Stay": '//*[@id="frmLogin"]/fieldset/p/label[2]',
        "LOGIN": '//*[@id="btnLogin"]',
        "PIN1": '//*[@id="txtScr11"]',
        "PIN2": '//*[@id="txtScr12"]',
        "PIN3": '//*[@id="txtScr13"]',
        "PIN4": '//*[@id="txtScr14"]',
        "PIN_done": '//*[@id="mtk_done"]',
        "Charge": '//*[@id="btnCshFrom"]',
        "inputCode": '//*[@id="wrap"]/div[1]/section/div/table/tbody/tr/td[2]',
        "amount": '//*[@id="wrap"]/div[1]/section/dl[1]/dd',
        "result": '//*[@id="wrap"]/div[1]/section/div/table/tbody/tr/td[3]',
        "menu": "/html/body/header/div/a[2]",
        "balance": "/html/body/div[4]/aside/div/div/section/div/div/dl[1]/dd[2]/p/span",
    },
}
active_count = 120


class simpleTelegram:
    def __init__(self, token: str, userid: str):
        self.telegram_req = "https://api.telegram.org/bot" + token + "/getUpdates"
        self.bot = telegram.Bot(token=token)
        self.userid = userid

    def sendMsg(self, msg: str) -> str:
        req = self.bot.send_message(chat_id=self.userid, text=str(msg))
        return req["message_id"]

    def delMsg(self, message_id: str):
        self.bot.delete_message(chat_id=self.userid, message_id=message_id)

    def sendPhoto(self, imgPth: str) -> str:
        try:
            req = self.bot.send_photo(chat_id=self.userid, photo=open(imgPth, "rb"))
        except Exception as e:
            req = self.sendMsg(msg=f"Error while sending photo: {e}")
        return req["message_id"]


def timechecker(times):
    while True:
        ttt = datetime.datetime.now()
        if times["opening"] <= ttt.time() <= times["hotclosing"]:
            time.sleep(times["delay_hot"])
            return True
        elif times["hotclosing"] <= ttt.time() <= times["closing"]:
            time.sleep(times["delay_nor"])
            return True
        elif not (times["opening"] <= ttt.time() <= times["closing"]):
            time.sleep(times["delay_off"])
            continue


def recv_pinCode(Tbot: simpleTelegram, times: dict) -> tuple:
    global active_count
    try:
        prevDate = requests.get(Tbot.telegram_req).json()["result"][-1]["message"][
            "date"
        ]
    except:
        prevDate = "0"
    abort = False
    while not abort:
        try:
            recvData = requests.get(Tbot.telegram_req).json()["result"][-1]["message"]
        except:
            recvData = {"date": "0"}
        try:
            if (
                (not recvData["date"] == prevDate)
                and (len(recvData["text"]) == 16 or len(recvData["text"]) == 18)
                and recvData["text"].isnumeric()
            ):
                abort = True
                active_count = times["active_count"]
            else:
                if active_count == 0:
                    timechecker(times)
                else:
                    time.sleep(2)
                    active_count -= 2
        except:
            continue
    result = (
        recvData["text"][0:4],
        recvData["text"][4:8],
        recvData["text"][8:12],
        recvData["text"][12:],
    )
    msg_id = Tbot.sendMsg(
        msg=f"PinCode received: {'-'.join(result)}\nRunning procedure..."
    )
    Tbot.delMsg(message_id=recvData["message_id"])
    return result, msg_id


def send_capcha(Tbot: simpleTelegram, img: str) -> str:
    prevDate = requests.get(Tbot.telegram_req).json()["result"][-1]["message"]["date"]
    last_capcha = Tbot.sendPhoto(imgPth=img)
    abort = False
    while not abort:
        recvData = requests.get(Tbot.telegram_req).json()["result"][-1]["message"]
        if (not recvData["date"] == prevDate) and (len(recvData["text"]) == 5):
            abort = True
        else:
            time.sleep(5)
    Tbot.delMsg(message_id=last_capcha)
    Tbot.delMsg(message_id=recvData["message_id"])
    return recvData["text"]


def set_chrome_driver(headless: bool):
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("lang=ko_KR")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--single-process")
            options.add_argument("--disable-dev-shm-usage")
            os.environ["WDM_LOG_LEVEL"] = "0"
        else:
            try:
                del os.environ["WDM_LOG_LEVEL"]
            except:
                None
        # driver = webdriver.Remote(
        #     command_executor=CHROME_PORT.replace("tcp", "http"), options=options
        # )
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.implicitly_wait(5)
        driver.set_window_size(800, 1000)
        return driver
    except Exception as e:
        print(e)
        return False


def cultureland_checkLoginStatus(config_data: dict, webdrv: webdriver.Chrome) -> bool:
    try:
        webdrv.get(config_data["login_url"])
        webdrv.find_element(By.XPATH, '//*[@id="txtScr11"]')
        print("Logged-in")
        return True
    except:
        print("Please Log-in")
        return False


def cultureland_doLogin(
    Tbot: simpleTelegram, config_data: dict, webdrv: webdriver.Chrome
):
    webdrv.save_screenshot(config_data["pic_capcha"])
    capchar = send_capcha(Tbot, config_data["pic_capcha"])
    print(f"Received capchar key: {capchar}")
    webdrv.find_element(By.XPATH, config_data["xpaths"]["capcha"]).send_keys(capchar)
    time.sleep(0.1)
    webdrv.find_element(By.XPATH, config_data["xpaths"]["ID"]).send_keys(
        config_data["ID"]
    )
    time.sleep(0.1)
    webdrv.find_element(By.XPATH, config_data["xpaths"]["PSSWD"]).click()
    time.sleep(0.1)
    inputVirtualKeypad(config_data["PSSWD"], config_data["xpaths"]["KEYPAD"], webdrv)
    webdrv.find_element(By.XPATH, config_data["xpaths"]["KEYPAD_done"]).click()
    time.sleep(0.1)
    webdrv.find_element(By.XPATH, config_data["xpaths"]["checkBox_ID"]).click()
    time.sleep(0.1)
    webdrv.find_element(By.XPATH, config_data["xpaths"]["checkBox_Stay"]).click()
    time.sleep(0.1)
    webdrv.find_element(By.XPATH, config_data["xpaths"]["LOGIN"]).click()


def inputVirtualKeypad(word: str, xpaths: str, webdrv: webdriver.Chrome):
    for key in list(word):
        if key == "^":
            webdrv.find_element(By.XPATH, xpaths + '특수키"]').click()
            time.sleep(0.1)
            webdrv.find_element(By.XPATH, xpaths + '꺽쇠"]').click()
        else:
            webdrv.find_element(By.XPATH, xpaths + key + '"]').click()
        time.sleep(0.1)


def chargePinCode(config_data: dict, pinCode: tuple, webdrv: webdriver.Chrome) -> bool:
    try:
        webdrv.find_element(By.XPATH, config_data["xpaths"]["PIN1"]).send_keys(
            pinCode[0]
        )
        time.sleep(0.1)
        webdrv.find_element(By.XPATH, config_data["xpaths"]["PIN2"]).send_keys(
            pinCode[1]
        )
        time.sleep(0.1)
        webdrv.find_element(By.XPATH, config_data["xpaths"]["PIN3"]).send_keys(
            pinCode[2]
        )
        time.sleep(0.1)
        inputVirtualKeypad(pinCode[3], config_data["xpaths"]["KEYPAD"], webdrv)
        webdrv.find_element(By.XPATH, config_data["xpaths"]["PIN_done"]).click()
        time.sleep(0.1)
        webdrv.find_element(By.XPATH, config_data["xpaths"]["Charge"]).click()
        time.sleep(0.1)
        return True
    except Exception as e:
        print(e)
        return False


def termWeb(webdrv: webdriver.Chrome):
    webdrv.quit()


def main(config_data: dict, times: dict):
    webdrv = None
    Tbot = simpleTelegram(config_data["my_token"], config_data["users_id"])
    Tbot.sendMsg("Bot is ready to receive")
    while True:
        pinCode, msg_id = recv_pinCode(Tbot=Tbot, times=times)
        if webdrv == None:
            webdrv = set_chrome_driver(True)
            if webdrv == False:
                Tbot.sendMsg(msg="Chrome did not prepared")
                return False
        webdrv.get(config_data["login_url"])
        cookies.load_cookies(webdrv, "cookie.pickle", None, False)
        ### Login Check
        trial_count = 0
        while not cultureland_checkLoginStatus(config_data, webdrv):
            trial_count += 1
            cultureland_doLogin(Tbot, config_data, webdrv)
            if trial_count > 10:
                # return False
                break
        cookies.save_cookies(webdrv, "cookie.pickle", None, False)
        req = chargePinCode(config_data, pinCode, webdrv)
        if not req:
            Tbot.sendMsg(msg="Charing the pincode has an error")
        else:
            ###check result
            result = [
                webdrv.find_element(By.XPATH, config_data["xpaths"]["inputCode"]).text,
                webdrv.find_element(By.XPATH, config_data["xpaths"]["amount"]).text,
                webdrv.find_element(By.XPATH, config_data["xpaths"]["result"]).text,
            ]
            webdrv.find_element(By.XPATH, config_data["xpaths"]["menu"]).click()
            result.append(
                webdrv.find_element(By.XPATH, config_data["xpaths"]["balance"]).text
            )
            print(result)
            if result[2] == "충전 완료":
                Tbot.delMsg(msg_id)
                Tbot.sendMsg(
                    f"{result[0]}를 통하여 {result[1]}을 충전하였습니다.\n잔액: {result[3]}원"
                )
            else:
                Tbot.delMsg(msg_id)
                Tbot.sendMsg(f"{result[0]}를 충전 실패: {result[2]}")
        cookies.save_cookies(webdrv, "cookie.pickle", None, False)
        if active_count <= 0:
            termWeb(webdrv)
            webdrv = None


def envToVar(config_data: dict, target: str) -> dict:
    try:
        config_data[target] = os.environ[target]
        print(f"Using {target} from environment variable")
        return True
    except KeyError:
        print(f"{target} is not in environment variable")
        return False


def env_timecheck(k: KeysView, target: str, org: datetime.time):
    TTT = org
    if target in k:
        try:
            TTT = datetime.datetime.strptime(os.environ[target], "%H%M")
        except:
            print(
                f"{os.environ[target]} is not the right format. {target} time will be used default value. ==> {org}"
            )
    return TTT


def env_delaycheck(k: KeysView, target: str, org: int):
    TTT = org
    if target in k:
        try:
            TTT = int(os.environ[target])
        except:
            print(
                f"{os.environ[target]} is not numeric. {target} will be used default value. ==> {org}"
            )
    return TTT


if __name__ == "__main__":
    problem = False
    if os.path.isfile("auth"):
        with open("auth", "rb") as f:
            import pickle

            temp = pickle.load(f)
        config_data.update(temp)
    else:
        for env in (
            "ID",
            "PSSWD",
            "my_token",
            "users_id",
        ):
            if not envToVar(config_data=config_data, target=env):
                print("Environment needed: " + env)
                problem = True
    ### If there is env ###
    envkeys = os.environ.keys()
    opening = env_timecheck(envkeys, "opening", datetime.time(8, 59, 0, 0))
    closing = env_timecheck(envkeys, "closing", datetime.time(22, 30, 0, 0))
    hotclosing = env_timecheck(envkeys, "hotclosing", datetime.time(16, 30, 0, 0))
    delay_nor = env_delaycheck(envkeys, "delay_nor", 60)
    delay_hot = env_delaycheck(envkeys, "delay_hot", 10)
    delay_off = env_delaycheck(envkeys, "delay_off", 10 * 60)
    active_count = env_delaycheck(envkeys, "active_count", 2 * 60)
    if not problem:
        main(
            config_data,
            {
                "opening": opening,
                "closing": closing,
                "hotclosing": hotclosing,
                "delay_nor": delay_nor,
                "delay_hot": delay_hot,
                "delay_off": delay_off,
                "active_count": active_count,
            },
        )
