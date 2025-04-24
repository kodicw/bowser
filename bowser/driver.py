from selenium import webdriver
from platform import freedesktop_os_release as os_release

system_os = os_release()["ID"].lower() if "ID" in os_release() else None


class Chrome:
    def __init__(self):
        opts = webdriver.ChromeOptions()
        match system_os:
            case "nixos":
                binary_path = "/run/current-system/sw/bin/google-chrome-stable"
                opts.binary_location = binary_path
                opts.add_argument("--ignore-certificate-errors")
                self.driver = webdriver.Chrome(options=opts)
                self.driver.set_page_load_timeout(120)
            case _:
                binary_path = "/usr/bin/chromium"
                opts.binary_location = binary_path
                opts.add_argument("--user-data-dir=user-data")
                opts.add_argument("--ignore-certificate-errors")
                opts.add_argument("--no-sandbox")
                opts.add_argument("--headless=new")
                driver = webdriver.Chrome(options=opts)
                driver.set_page_load_timeout(20)
                self.driver = driver


if __name__ == "__main__":
    Chrome().driver.get("http://google.com")
