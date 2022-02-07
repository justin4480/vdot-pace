import unittest
from pace import GetPace

def run_tests(test_class):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)


class TestGetPace(unittest.TestCase):

    def setUp(self):
        None
        
    def tearDown(self):
        None

    def test_get_min_per_distance_vdot(self):
        self.assertRaises(TypeError, GetPace.get_min_per_distance, "50", 'm', 'km')
        self.assertRaises(ValueError, GetPace.get_min_per_distance, 29, 'm', 'mi')
        self.assertRaises(ValueError, GetPace.get_min_per_distance, 87, 'm', 'mi')

    def test_get_min_per_distance_intensity(self):
        self.assertRaises(ValueError, GetPace.get_min_per_distance, 50, 'a', 'km')
        self.assertRaises(ValueError, GetPace.get_min_per_distance, 50, 1, 'km')

    def test_get_min_per_distance_km_mi(self):
        self.assertRaises(ValueError, GetPace.get_min_per_distance, 50, 'm', 'k')
        self.assertRaises(ValueError, GetPace.get_min_per_distance, 50, 'm', 'mile')

    def test_get_min_per_distance_m(self):
        self.assertEqual(GetPace.get_min_per_distance(30, 'm', 'km'), "7:04")
        self.assertEqual(GetPace.get_min_per_distance(30, 'm', 'mi'), "11:23")
        self.assertEqual(GetPace.get_min_per_distance(50, 'm', 'km'), "4:31")
        self.assertEqual(GetPace.get_min_per_distance(50, 'm', 'mi'), "7:17")
        self.assertEqual(GetPace.get_min_per_distance(85, 'm', 'km'), "2:52")
        self.assertEqual(GetPace.get_min_per_distance(85, 'm', 'mi'), "4:37")

    def test_get_min_per_distance_t(self):
        self.assertEqual(GetPace.get_min_per_distance(30, 't', 'km'), "6:25")
        self.assertEqual(GetPace.get_min_per_distance(30, 't', 'mi'), "10:20")
        self.assertEqual(GetPace.get_min_per_distance(50, 't', 'km'), "4:15")
        self.assertEqual(GetPace.get_min_per_distance(50, 't', 'mi'), "6:50")
        self.assertEqual(GetPace.get_min_per_distance(85, 't', 'km'), "2:46")
        self.assertEqual(GetPace.get_min_per_distance(85, 't', 'mi'), "4:27")

    def test_get_min_per_distance_i(self):
        self.assertEqual(GetPace.get_min_per_distance(30, 'i', 'km'), "5:54")
        self.assertEqual(GetPace.get_min_per_distance(30, 'i', 'mi'), "9:28")
        self.assertEqual(GetPace.get_min_per_distance(50, 'i', 'km'), "3:55")
        self.assertEqual(GetPace.get_min_per_distance(50, 'i', 'mi'), "6:12")
        self.assertEqual(GetPace.get_min_per_distance(85, 'i', 'km'), "2:33")
        self.assertEqual(GetPace.get_min_per_distance(85, 'i', 'mi'), "3:03")

run_tests(TestGetPace)
