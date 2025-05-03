import unittest
from utils import build_structured_prompt, build_natural_prompt

class TestUtils(unittest.TestCase):
    def test_build_structured_prompt(self):
        role = "Python Developer"
        task = "write a function to sort a list"
        constraints = "Use the built-in sorted function"
        output = "code with comments"
        personality = "experienced professional"
        
        prompt = build_structured_prompt(role, task, constraints, output, personality)
        
        self.assertIn(role, prompt)
        self.assertIn(task, prompt)
        self.assertIn(constraints, prompt)
        self.assertIn(output, prompt)
        self.assertIn(personality, prompt)
    
    def test_build_natural_prompt(self):
        role = "Python Developer"
        task = "write a function to sort a list"
        constraints = "Use the built-in sorted function"
        output = "code with comments"
        personality = "experienced professional"
        
        prompt = build_natural_prompt(role, task, constraints, output, personality)
        
        self.assertIn(role, prompt)
        self.assertIn(task, prompt)
        self.assertIn(constraints, prompt)
        self.assertIn(output, prompt)
        self.assertIn(personality, prompt)

if __name__ == '__main__':
    unittest.main() 