import unittest
from app import create_app
from extensions import db
from models import User, Prompt
from werkzeug.security import check_password_hash

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_model(self):
        # Test creating a user
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # Test password hashing
        self.assertTrue(check_password_hash(user.password_hash, 'password123'))
        self.assertFalse(check_password_hash(user.password_hash, 'wrong_password'))
    
    def test_prompt_model(self):
        # Create a test prompt
        prompt = Prompt(
            title='Test Prompt',
            role='Developer',
            task='Write code',
            constraints='Use Python',
            output='Code with comments',
            personality='Professional',
            structured_prompt='Structured content',
            natural_prompt='Natural content',
            is_public=True,
            tags='python,coding,test',
            user_id=self.user.id
        )
        db.session.add(prompt)
        db.session.commit()
        
        # Test retrieving the prompt
        saved_prompt = Prompt.query.filter_by(title='Test Prompt').first()
        self.assertIsNotNone(saved_prompt)
        self.assertEqual(saved_prompt.role, 'Developer')
        self.assertEqual(saved_prompt.tags, 'python,coding,test')
        self.assertTrue(saved_prompt.is_public)
        
        # Test the relationship with user
        self.assertEqual(saved_prompt.author, self.user)
        
        # Test user's prompts relationship
        user_prompts = self.user.prompts.all()
        self.assertEqual(len(user_prompts), 1)
        self.assertEqual(user_prompts[0], prompt)

if __name__ == '__main__':
    unittest.main() 