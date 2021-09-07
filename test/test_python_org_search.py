import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("https://odissine.pythonanywhere.com/")
        self.assertIn("La petite pépinière", driver.title)

        # On selectionne la première espèce disponible
        select = Select(driver.find_element_by_id('espece')).select_by_index(1)

        # On clique sur le bouton Rechercher
        driver.find_element_by_id("search-btn").click()

        # On récupère la valeur html de la balise (x produits) et on test si la valeur est supérieur ou égale à 0
        qty_label = driver.find_element_by_id("qty_find_product").text
        qty = int(qty_label[0:-9])
        print(qty_label)
        print(qty)
        assert qty >= 0

        # elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source

    def test_login(self):
        driver = self.driver

        # On clique sur le bouton Login
        driver.find_element_by_id("login-btn").click()

        username_element = driver.find_element_by_id("username")
        pwd_element = driver.find_element_by_id("password")

        username_element.send_keys("cyrilhenry")
        pwd_element.send_keys("Azerty2+")
        pwd_element.send_keys(Keys.RETURN)

        qty_order_label = driver.find_element_by_id("qty-find-order").text
        qty_order = int(qty_order_label[0:-9])
        print(qty_order_label)
        print(qty_order)
        assert qty_order >= 0

        assert "No results found." not in driver.page_source

    def test_url_bidon(self):
        driver = self.driver
        driver.get("https://odissine.pythonanywhere.com/pageinconnue")
        self.assertIn("Page introuvable (Erreur 404)", driver.find_element_by_id("title-error-text").text)

        assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
