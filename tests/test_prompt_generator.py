import unittest
from services.prompt_generator import generate_ai_prompt

class TestPromptGenerator(unittest.TestCase):
    def test_prompt_contains_fail_safe_instructions(self):
        """
        Verify that the generated prompt includes the Fail-Safe / Grace Period instructions.
        """
        prompt = generate_ai_prompt("app_id", "app_name", "app_secret", "http://api.url")

        self.assertIn("## 7. Mise en Cache et Résilience (Fail-Safe)", prompt)
        self.assertIn("Mode Hors-Ligne Toléré (Grace Period)", prompt)
        self.assertIn("72 heures", prompt)
        self.assertIn("Au-delà de 72 heures sans contact avec le serveur, l'application se verrouille.", prompt)

if __name__ == '__main__':
    unittest.main()
