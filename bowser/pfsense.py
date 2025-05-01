from bowser.website import Website, Job
from selenium.webdriver.common.by import By
from bowser.logs import logger


class Pfsense(Website):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = f"https://{host}:{port}"
        super().__init__(self.base_url)

    def login(self) -> None:
        """This will login using self.username and self.password. Do not use this if you are already logged in"""
        self.run(
            Job(
                page="/index.php",
                actions=[
                    {
                        "id": "usernamefld",
                        "method": "send_keys",
                        "value": self.username,
                    },
                    {
                        "id": "passwordfld",
                        "method": "send_keys",
                        "value": self.password,
                    },
                    {
                        "xpath": "//*[@name='login']",
                        "method": "click",
                    },
                ],
            )
        )

    def save(self):
        """Convenience method. This will not work in all cases"""
        self.run(Job(actions=[{"id": "save", "method": "click"}]))

    def apply(self):
        """Convenience method. This will not work in all cases"""
        self.run(Job(actions=[{"xpath": "//*[@name='apply']", "method": "click"}]))

    def add_dns_forwarders(
        self,
        domains: list[str],
        dns_server: str = "1.1.1.1",
        description: str = "Added by robots",
    ):
        for domain in domains:
            if self.page_contains("/services_dnsmasq.php", domain):
                logger.info(f"Domain forwarder already exists {domain}")
                continue
            self.run(
                Job(
                    page="/services_dnsmasq_domainoverride_edit.php",
                    actions=[
                        {"id": "domain", "method": "send_keys", "value": domain},
                        {
                            "id": "ip",
                            "method": "send_keys",
                            "value": dns_server,
                        },
                        {
                            "id": "descr",
                            "method": "send_keys",
                            "value": description,
                        },
                    ],
                )
            )
            self.save()
            logger.info(f"Added DNS forwarder {domain=}, {dns_server=}, {description=}")

    def add_ip_to_alias(self, ip, description="") -> None:
        addresses = [
            address.get_attribute("value")
            for address in self.driver.find_elements(
                By.XPATH, "//input[@class='form-control ui-autocomplete-input']"
            )
        ]

        addresses_list_size = len(addresses)

        if ip in addresses:
            return

        self.run(
            Job(
                actions=[
                    {
                        "id": "addrow",
                        "method": "click",
                    },
                    {
                        "id": f"address{addresses_list_size}",
                        "method": "send_keys",
                        "value": ip,
                    },
                    {
                        "id": f"detail{addresses_list_size}",
                        "method": "send_keys",
                        "value": description,
                    },
                ],
            )
        )

    def get_alias_edit_page(self, name: str) -> str | None:
        result = self.driver.find_element(By.XPATH, f"//td[contains(.,'{name}')]")
        result = result.get_attribute("ondblclick")

        if result is not None:
            return result.split("='")[1].replace("';", "")
        return None

    def add_ip_alias(
        self, name: str, ips: list[str], description: str = "added by robots"
    ):
        if not self.page_contains("/firewall_aliases.php", name):
            logger.info(f"Alias already exists {name}")
            self.run(
                Job(
                    page="/firewall_aliases_edit.php?tab=ip",
                    actions=[
                        {
                            "id": "name",
                            "method": "send_keys",
                            "value": name,
                        },
                        {
                            "id": "descr",
                            "method": "send_keys",
                            "value": description,
                        },
                    ],
                )
            )
            page = self.get_alias_edit_page(name)
            if page is None:
                raise ValueError

            self.driver.get(self.base_url + "/" + page)
            for ip in ips:
                self.add_ip_to_alias(ip)
            self.save()

        else:
            page = self.get_alias_edit_page(name)
            if page is None:
                raise ValueError

            self.driver.get(self.base_url + "/" + page)
            for ip in ips:
                self.add_ip_to_alias(ip)
            self.save()
        self.apply()

    def is_package_installed(self, package: str):
        self.driver.get(self.base_url + "/pkg_mgr_installed.php")
        self.wait_for_element(
            "xpath", "//*[@class='table table-striped table-hover table-condensed']"
        )
        if self.page_contains(page="", item=package.lower()):
            logger.info(f"{package=} installed")
            return True
        else:
            logger.info(f"{package=} not installed")
            return False

    def is_package_available(self, package: str):
        self.driver.get(self.base_url + "/pkg_mgr.php")
        self.wait_for_element("xpath", "//*[@title='Click to install']")
        if self.page_contains(page="", item=f"{package}".lower()):
            logger.info(f"{package=} is available")
            return True
        else:
            logger.info(f"{package=} not available")
            return False

    def install_package(self, package):
        if not self.is_package_installed(package) and self.is_package_available(
            package
        ):
            self.run(
                Job(
                    page=f"/pkg_mgr_install.php?pkg=pfSense-pkg-{package}",
                    actions=[{"id": "pkgconfirm", "method": "click"}],
                )
            )
            self.wait_for_element(
                "xpath",
                "//*[@class='progress-bar progress-bar-striped progress-bar-success']",
            )
            if (
                "installation successfully completed."
                in self.driver.find_element(By.ID, "final").text
            ):
                logger.info(f"{package=} installation successfully completed.")
        else:
            logger.info(f"{package=} installed or not available")
