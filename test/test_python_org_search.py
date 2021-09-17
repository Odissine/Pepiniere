import unittest
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# base_url = "https://odissine.pythonanywhere.com/"
base_url = "http://127.0.0.1:8000/"


class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get(base_url)
        self.assertIn("La petite pépinière", driver.title)

        # On selectionne la première espèce disponible
        select = Select(driver.find_element_by_id('espece')).select_by_index(1)

        # On clique sur le bouton Rechercher
        driver.find_element_by_id("search-btn").click()

        # On récupère la valeur html de la balise (x produits) et on test si la valeur est supérieur ou égale à 0
        qty_label = driver.find_element_by_id("qty_find_product").text
        qty = int(qty_label[0:-9])
        self.assertGreaterEqual(qty, 0, "ERROR : No product found !")
    '''
    def test_login(self):
        driver = self.driver

        # On clique sur le bouton Login
        driver.find_element_by_id("login_btn").click()

        username_element = driver.find_element_by_id("username")
        pwd_element = driver.find_element_by_id("password")

        username_element.send_keys("cyrilhenry")
        pwd_element.send_keys("Azerty2+")
        pwd_element.send_keys(Keys.RETURN)

        qty_order_label = driver.find_element_by_id("qty-find-order").text
        qty_order = int(qty_order_label[0:-9])
        print(qty_order_label)
        print(qty_order)
        self.assertGreaterEqual(qty_order, 0, "ERROR : No product found !")

        assert "No results found." not in driver.page_source
    '''

    def test_url_bidon(self):
        driver = self.driver
        driver.get(base_url + "pageinconnue/")
        self.assertEqual("Page introuvable (Erreur 404)", driver.find_element_by_id("title-error-text").text,"ERROR : 404 Page doesn't appear")

    def test_url_admin(self):
        driver = self.driver

        urls = ["order/list", "order/detail/1", "cart/", "order/print/23?download=1&mode=2"]
        for url in urls:
            driver.get(base_url + url)
            test_url = str(base_url + url)
            current_url = driver.current_url
            self.assertNotEqual(current_url, test_url, "ERROR : Admin access permitted for lambda user !")

        assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
