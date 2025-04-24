from bowser.driver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from typing import Callable
from bowser.logs import logger


class Job:
    def __init__(self, page: str = "", actions: list[dict] = [{}]):
        self.page = page
        self.actions = actions


class Website(Chrome):
    def __init__(self, base_url: str):
        self.base_url: str = base_url
        self.jobs: list[Job] = []
        super().__init__()

    def load_action(
        self, action: dict
    ) -> WebElement | None | tuple | Callable[[], None]:
        """This will return a function or tuple(function, arg) given an action. If all fails it will return None"""
        result = None
        for selector in [By.CSS_SELECTOR, By.ID, By.XPATH]:
            if str(selector) in action:
                try:
                    result = self.driver.find_element(selector, action[str(selector)])
                except Exception as e:
                    logger.warning(f"Could not find element by {selector=}")
                    logger.error(e)

        if result is None:
            return None

        match action["method"]:
            case "click":
                return result.click
            case "send_keys":
                return (result.send_keys, action["value"])
            case "select":
                result = Select(result)
                return (result.select_by_visible_text, action["value"])

        logger.warning(f"Failed to load {action=}")
        return None

    def load_job(self, job: Job):
        self.jobs.append(job)

    def load_jobs(self, jobs: list[Job]):
        for job in jobs:
            self.jobs.append(job)

    def run(self, job: Job):
        self.driver.get(self.base_url + job.page) if job.page != "" else None
        for action in job.actions:
            action = self.load_action(action)
            if action is None:
                continue
            elif isinstance(action, tuple) and len(action) > 1:
                _action = action[0]
                arg = action[1]
                _action(arg)
            elif hasattr(action, "__call__"):
                action()

    def run_all_jobs(self):
        for job in self.jobs:
            self.driver.get(self.base_url + job.page)
            for action in job.actions:
                action = self.load_action(action)
                if action is None:
                    continue
                elif isinstance(action, tuple) and len(action) > 1:
                    _action = action[0]
                    arg = action[1]
                    _action(arg)
                elif hasattr(action, "__call__"):
                    action()

    def page_contains(self, page: str, item: str, case=False) -> bool:
        self.driver.get(self.base_url + page)
        page_source = (
            self.driver.page_source.lower() if case else self.driver.page_source
        )
        if item in page_source:
            return True
        else:
            return False


if __name__ == "__main__":
    s = Website("https://automationintesting.com")
    s.load_jobs(
        [
            Job(
                page="/selenium/testpage/",
                actions=[
                    {
                        "xpath": "//input[@id='firstname']",
                        "method": "send_keys",
                        "value": "test",
                    },
                    {
                        "id": "checkbox2",
                        "method": "click",
                    },
                    {"id": "surname", "method": "send_keys", "value": "test"},
                    {"id": "gender", "method": "select", "value": "Male"},
                ],
            ),
        ]
    )

    import time

    s.run_all_jobs()
    time.sleep(5)
