import unittest
import MSFO_script

class Test_test_1(unittest.TestCase):
    def setUp(self):
        MSFO_script.ticker = MSFO_script.Ticker()
        MSFO_script.filename = str()
        MSFO_script.pages = list()
        MSFO_script.measure_unit = int()
        MSFO_script.amount_line = str()
        MSFO_script.method = str()

    def test_magnit_parsing(self):
        url = "https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf"
        print("magnit_parsing")
        result = MSFO_script.run(url, "mgnt", "p")
        self.assertEqual(result[0], 4)
        self.assertTrue(result[1] != 0)
        self.assertTrue(result[2] != 0)
    
    def test_mts_parsing(self):
        url = "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf"
        print("mts_parsing")
        result = MSFO_script.run(url, "mtss", "p")
        self.assertEqual(result[0], 4)
        self.assertTrue(result[1] != 0)
        self.assertTrue(result[2] != 0)
        
    def test_rushydro_parsing(self):
        url = "http://www.rushydro.ru/upload/iblock/89e/IFRS-RusHydro_2112_rrus.pdf"
        print("hydro_parsing")
        result = MSFO_script.run(url, "hydr", "p")
        self.assertEqual(result[0], 4)
        self.assertTrue(result[1] != 0)
        self.assertTrue(result[2] != 0)
    
    def test_magnit_tinkoff_api(self):
        url = "https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf"
        print("magnit_tinkoff")
        result = MSFO_script.run(url, "mgnt", "t")
        self.assertEqual(result[0], 4)
        self.assertTrue(result[1] != 0)
        self.assertTrue(result[2] != 0)
    
    def test_mts_tinkoff_api(self):
        url = "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf"
        print("mts_tinkoff")
        result = MSFO_script.run(url, "mtss", "t")
        self.assertEqual(result[0], 4)
        self.assertTrue(result[1] != 0)
        self.assertTrue(result[2] != 0)
        
    def test_rushydro_tinkoff_api(self):
        url = "http://www.rushydro.ru/upload/iblock/89e/IFRS-RusHydro_2112_rrus.pdf"
        print("hydro_tinkoff")
        result = MSFO_script.run(url, "hydr", "t")
        self.assertEqual(result[0], 4)
        self.assertTrue(result[1] != 0)
        self.assertTrue(result[2] != 0)


if __name__ == '__main__':
    unittest.main()
