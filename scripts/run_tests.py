import sys, unittest

if __name__ == '__main__':
    print("Running CourierAI Test Suite...")
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
