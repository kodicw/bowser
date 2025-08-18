from selenium import webdriver
from platform import freedesktop_os_release as os_release
import tempfile
import shutil

try:
    system_os = os_release()["ID"].lower() if "ID" in os_release() else None
except Exception as e:
    print(str(e))


class Chrome:
    def __init__(self, headless: bool = False, proxy: str | None = None):
        opts = webdriver.ChromeOptions()
        match system_os:
            case "nixos":
                binary_path = (
                    shutil.which("chromium")
                    or "/run/current-system/sw/bin/google-chrome-stable"
                )
                if proxy:
                    opts.add_argument(f"--proxy-server={proxy}")

                opts.binary_location = binary_path
                opts.add_argument("--ignore-certificate-errors")
                opts.add_argument("--headless=new") if headless else None
                self.driver = webdriver.Chrome(options=opts)
                self.driver.set_page_load_timeout(120)
            case _:
                user_data_dir = tempfile.mkdtemp(dir="/tmp")
                binary_path = shutil.which("chromium")
                opts.binary_location = binary_path or "/usr/bin/chromium"
                opts.add_argument(f"--user-data-dir={user_data_dir}")
                opts.add_argument("--ignore-certificate-errors")
                opts.add_argument("--no-sandbox")
                opts.add_argument("--disable-dev-shm-usage")
                opts.add_argument("--headless=new")
                driver = webdriver.Chrome(options=opts)
                driver.set_page_load_timeout(20)
                self.driver = driver

    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":
    Chrome().driver.get("http://google.com")
