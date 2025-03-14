#!/usr/bin/env python3
"""
Script to run specific tests for the voice control system.
"""
import unittest
from test_voice_control import (
    TestCommandInterpreter,
    TestCommandExecutor,
    TestVoiceControlSystem,
    TestOptimizedVoiceControlSystem
)

if __name__ == "__main__":
    # Create a test suite with specific test classes
    suite = unittest.TestSuite()
    
    # Add test classes to the suite
    suite.addTest(unittest.makeSuite(TestCommandInterpreter))
    suite.addTest(unittest.makeSuite(TestCommandExecutor))
    suite.addTest(unittest.makeSuite(TestVoiceControlSystem))
    suite.addTest(unittest.makeSuite(TestOptimizedVoiceControlSystem))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
