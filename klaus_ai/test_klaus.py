import unittest
from voice_interface import VoiceEngine
from skills import Skills

class TestKlaus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.voice = VoiceEngine()
        cls.skills = Skills()

    def test_voice_initialization(self):
        """Test voice engine loads"""
        self.assertTrue(hasattr(self.voice, 'engine'))
        
    def test_calculation_skill(self):
        response = self.skills.handle_command("15 * 4")  # Simpler command
        self.assertIn("60", response)

    def test_email_parsing(self):
        result = self.skills.handle_email_command("dummy command send email to test@test.com about hello")
        self.assertIn("test@test.com", result)

if __name__ == '__main__':
    unittest.main()