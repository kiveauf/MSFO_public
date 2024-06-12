import unittest
import MSFO_script
from DocsTest import docs

class Test_test_1(unittest.TestCase):
    def setUp(self):
        MSFO_script.ticker = MSFO_script.Ticker()
        MSFO_script.filename = str()
        MSFO_script.pages = list()
        MSFO_script.measure_unit = int()
        MSFO_script.amount_line = str()


    @unittest.skip   
    def test_magnit_parsing(self):
        url = docs[0]
        print("magnit_parsing")
        result = MSFO_script.run(url, "mgnt")
        #self.assertEqual(result[0], 4)
        self.assertTrue(result[0] != 0)
        self.assertTrue(result[1] != 0)

   
    def test_mts_parsing(self):
        url = docs[1]
        print("mts_parsing")
        result = MSFO_script.run(url, "mtss")
        #self.assertEqual(result[0], 4)
        self.assertTrue(result[0] != 0)
        self.assertTrue(result[1] != 0)


    @unittest.skip    
    def test_rushydro_parsing(self):
        url = docs[4]
        print("hydro_parsing")
        result = MSFO_script.run(url, "hydr")
        #self.assertEqual(result[0], 4)
        self.assertTrue(result[0] != 0)
        self.assertTrue(result[1] != 0)
    

    @unittest.skip    
    def test_magnit_tinkoff_api(self):
        url = docs[0]
        print("magnit_tinkoff")
        result = MSFO_script.run(url, "mgnt", "t")
        #self.assertEqual(result[0], 4)
        self.assertTrue(result[0] != 0)
        self.assertTrue(result[1] != 0)
    

    def test_mts_tinkoff_api(self):
        url = docs[1]
        print("mts_tinkoff")
        result = MSFO_script.run(url, "mtss", "t")
        #self.assertEqual(result[0], 4)
        self.assertTrue(result[0] != 0)
        self.assertTrue(result[1] != 0)
    
    
    @unittest.skip   
    def test_rushydro_tinkoff_api(self):
        url = docs[4]
        print("hydro_tinkoff")
        result = MSFO_script.run(url, "hydr", "t")
        #self.assertEqual(result[0], 4)
        self.assertTrue(result[0] != 0)
        self.assertTrue(result[1] != 0)


if __name__ == '__main__':
    unittest.main()
