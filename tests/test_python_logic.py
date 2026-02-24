import unittest
from src.state_manager import StateManager, GameState

class MockState(GameState):
    def __init__(self, manager, name):
        super().__init__(manager)
        self.name = name

class TestPythonLogic(unittest.TestCase):
    def setUp(self):
        self.manager = StateManager()

    def test_stack_lifecycle(self):
        state_a = MockState(self.manager, "StateA")
        state_b = MockState(self.manager, "StateB")
        
        # Test Push
        self.manager.push(state_a)
        self.assertEqual(self.manager.peek().name, "StateA")
        
        self.manager.push(state_b)
        self.assertEqual(self.manager.peek().name, "StateB")
        
        # Test Pop
        popped = self.manager.pop()
        self.assertEqual(popped.name, "StateB")
        self.assertEqual(self.manager.peek().name, "StateA")
        
        self.manager.pop()
        self.assertIsNone(self.manager.peek())

    def test_pop_empty(self):
        result = self.manager.pop()
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
