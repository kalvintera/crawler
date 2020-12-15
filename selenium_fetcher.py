import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import CHROME_DRIVER_PATH


class ScraperSelenium:
    """
    Uses Selenium to request web content to handle buttons and iframes.
    """

    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = None
        self.start()

    def __call__(self):
        """
        Start webdriver.
        """
        self.start()

    def start(self):
        # try to instantiate chrome for a max. of 25 times
        print("ScraperSelenium.start():")
        self.quit()
        for i in range(25):
            try:
                self.driver = webdriver.Chrome(options=self.options, executable_path=CHROME_DRIVER_PATH)
            except Exception as e:
                print("\tFailed instanciation attempt %s/25" % (i + 1))
                print("\tChrome error:", e)
                self.driver = None
            else:
                print("\t Chrome driver started successfully.")
                break

    def quit(self):
        """
        Quit webdriver.
        """
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

    @staticmethod
    def write(html):
        """
        This function writes html content to disk. Useful to test different html parsers.
        """
        with open(f"html_{datetime.today()}.html", "w") as f:
            f.write(html)

    def request_selenium(self, url, button=None, iframe=None, body=None):
        """
        This function is able to switch iframes and click buttons (e.g. in case of cookie prompts) to retrieve a
        websites' html content.

        Arguments:
            url(str): url to website.
            button(dict or str): name of the button and type of syntax to find it, e.g.(XPATH, CSS,...).
            iframe(dict or str): name of the button's iframe and type of syntax e.g.(XPATH, CSS,...).
            body(dict or str or int): name of an element that should be loaded or wait time in seconds,
                                      before accessing the page source.
        """

        try:
            self.driver.get(url)
            print("request_selenium(): ", url)
            # select iframe
            if iframe:
                iframe_params = (iframe["element"], iframe["by"]) if isinstance(iframe, dict) else (iframe, None)
                self.wait_locate(*iframe_params)
                self.switch_frame(*iframe_params)

            # click button
            if button:
                button_params = (button["element"], button["by"]) if isinstance(button, dict) else (button, None)
                # btn = \
                self.wait_click(*button_params)
                # btn.click()

            # make sure to select html body before returning driver.page_source
            self.driver.switch_to.default_content()

            # wait until html body is fully loaded
            if body:
                if isinstance(body, int):
                    time.sleep(body)
                else:
                    body_params = (body["element"], body["by"]) if isinstance(body, dict) else (body, None)
                    self.wait_locate(*body_params)

            # print("request_selenium(): Active window handles:", self.driver.window_handles)
            return self.driver.page_source

        except Exception as e:
            print("Selenium error", e)
            return ""

    def switch_frame(self, element, by="ID"):
        """
        Switches the selenium web driver to the specified iframe within a webpage.

        Arguments:
            element(str): iframe element to look for.
            by(str): Syntax (e.g. XPATH, CSS,...) that shall be used to find iframe element.
        """
        if by == "ID" or by == "NAME" or by is None:
            iframe = element
        elif by == "XPATH":
            iframe = self.driver.find_element_by_xpath(element)
        elif by == "CLASS":
            iframe = self.driver.find_elements_by_class_name(element)
        elif by == "LINK_TEXT":
            iframe = self.driver.find_element_by_link_text(element)
        else:
            print("switch_frame(): wrong value for 'by':", by)
            return
        self.driver.switch_to.frame(iframe)

    def wait_locate(self, element, by="ID"):
        """
        Waits max. 10 seconds until an element within a webpage is loaded.

        Arguments:
            element(str): Element to wait for.
            by(str): Syntax (e.g. XPATH, CSS,...) that shall be used to find the element.

        Returns:
            Selenium element that was located within the webpage.
        """
        syntax = self.select_syntax(by)
        if syntax:
            wait = WebDriverWait(self.driver, 10)
            return wait.until(EC.presence_of_element_located((syntax, element)))
        else:
            print("wait_locate(): wrong value for 'by':", by)
            return None

    def wait_click(self, element, by="ID"):
        """
        Waits to click an element on a webpage.

        Arguments:
            element(str): Element to click.
            by(str): Syntax (e.g. XPATH, CSS,...) that shall be used to find the element.
        """
        syntax = self.select_syntax(by)
        if syntax:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.element_to_be_clickable((syntax, element))).click()
            wait.until(EC.invisibility_of_element_located((syntax, element)))
            print("wait_click(): Button clicked.")
        else:
            print("wait_click(): wrong value for 'by':", by)

    @staticmethod
    def select_syntax(by="ID"):
        """
        Returns the selenium common.by syntax to locate elements.
        If by is set to None, By.ID is returned as default.

        Arguments:
            by(str): Valid values: ID, XPATH, CLASS, LINK_TEXT, CSS

        Returns:
            common.by syntax for Selenium.
        """
        by_dict = {"ID": By.ID,
                   "XPATH": By.XPATH,
                   "CLASS": By.CLASS_NAME,
                   "LINK_TEXT": By.LINK_TEXT,
                   "CSS": By.CSS_SELECTOR}
        return by_dict["ID"] if by is None else by_dict[by] if by in by_dict.keys() else None