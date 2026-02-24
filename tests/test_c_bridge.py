import unittest
import ctypes
import os

# --- Structure Definitions (Synced with Engine) ---
class AABB(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("w", ctypes.c_float), ("h", ctypes.c_float)]

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

class TestCBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lib_path = os.path.join(os.getcwd(), "libengine.dylib")
        cls.engine = ctypes.CDLL(lib_path)
        
        # Define argtypes/restypes
        cls.engine.check_collision_aabb.argtypes = [AABB, AABB]
        cls.engine.check_collision_aabb.restype = ctypes.c_int
        
        cls.engine.find_path.argtypes = [
            ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(Point), ctypes.c_int
        ]
        cls.engine.find_path.restype = ctypes.c_int

    def test_collision_positive(self):
        box_a = AABB(0, 0, 1, 1)
        box_b = AABB(0.5, 0.5, 1, 1)
        result = self.engine.check_collision_aabb(box_a, box_b)
        self.assertEqual(result, 1, "Expected collision at (0.5, 0.5)")

    def test_collision_negative(self):
        box_a = AABB(0, 0, 1, 1)
        box_b = AABB(2, 2, 1, 1)
        result = self.engine.check_collision_aabb(box_a, box_b)
        self.assertEqual(result, 0, "Expected no collision between distant boxes")

    def test_pathfinding_short(self):
        # 3x3 Grid (all walkable)
        grid = (ctypes.c_int * 9)(0,0,0, 0,0,0, 0,0,0)
        path = (Point * 10)()
        # From (0,0) to (2,2)
        length = self.engine.find_path(grid, 3, 3, 0, 0, 2, 2, path, 10)
        self.assertGreater(length, 0, "Should find a path in open grid")
        self.assertEqual(path[length-1].x, 2)
        self.assertEqual(path[length-1].y, 2)

if __name__ == "__main__":
    unittest.main()
