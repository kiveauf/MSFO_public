import unittest

from dungeon import play

class Test(unittest.TestCase):
   
    def test_1111111(self):
         result = play(["1","1","1","1","1","1","1","1","1","1","1"])
         self.assertEqual(result, [279, 10167456])

    def test_1111111_with_random_shit(self):
        result = play(["-2", "1", "10", "1", "1", "5", "1", "A", "1", "r", "1", "1", "1", "1", "90", "1", "1"])
        self.assertEqual(result, [279, 10167456])

    def test_311111(self):
        result = play(["3","1","1","1", "1", "1"])
        self.assertEqual(result, [65, 461398980])

    def test_11111_quit(self):
         result = play(["1","1","1","1","1","2"])
         self.assertEqual(result, [50, 894167480])

    

if __name__ == '__main__':
    unittest.main()
    #print(__name__)

