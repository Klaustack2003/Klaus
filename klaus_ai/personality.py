import random

class PersonalityEngine:
    def __init__(self):
        self.traits = {
            "humor_level": 3,  # 1-5 scale
            "formality": 3,    # 1-5 scale
            "enthusiasm": 4    # 1-5 scale
        }
        
    def adjust_response(self, response):
        """Modify responses based on personality traits"""
        if not response:
            return response
            
        # Don't modify error messages
        if "error" in response.lower() or "sorry" in response.lower():
            return response
            
        # Apply personality adjustments
        if self.traits["humor_level"] > 3 and len(response.split()) > 5:
            response = self.add_humor(response)
            
        if self.traits["formality"] < 3:
            response = self.casualize(response)
            
        if self.traits["enthusiasm"] > 3:
            response = self.add_enthusiasm(response)
            
        return response
    
    def add_humor(self, response):
        """Add witty remarks occasionally"""
        if random.random() > 0.7:  # 30% chance to add humor
            humorous_endings = [
                " By the way, that's what I do best!",
                " Easy peasy lemon squeezy!",
                " Piece of cake!",
                " I live for these moments!",
                " Another victory for team human-Klaus!"
            ]
            response += random.choice(humorous_endings)
        return response
    
    def casualize(self, response):
        """Make formal language more casual"""
        replacements = {
            "certainly": "sure",
            "I can assist": "I can help",
            "please": "",
            "kindly": "",
            "would you like": "do you want"
        }
        for formal, casual in replacements.items():
            response = response.replace(formal, casual)
        return response
    
    def add_enthusiasm(self, response):
        """Add energetic expressions"""
        if random.random() > 0.5:  # 50% chance to add enthusiasm
            enthusiastic_starters = [
                "Awesome! ",
                "Great! ",
                "Perfect! ",
                "Got it! ",
                "Absolutely! "
            ]
            response = random.choice(enthusiastic_starters) + response
        return response