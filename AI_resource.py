from transformers import pipeline

class Chatbot:
    def __init__(self):
        # Initialize the text-generation pipeline
        self.chatbot = pipeline(task="text-generation", model="facebook/blenderbot-400M-distill")
        
        # Predefined keyword-based responses stored in a dic
        self.keyword_responses = {
            "veteran": "Veterans Affairs Supportive Housing Voucher Program provides assistance to veterans in need.",
            "Children" or "youth": "The Relative",
            "Violence": "Center of Hope",
            "Female" and "single": "My Sister's House",
            "families" or "family": "Charlotte Family Housing",
            "drugs" or "alcohol": "Adult Rehabilitation Center"
           
        }

    def generate_response(self, prompt):
        # Check for predefined keyword matches
        for keyword, response in self.keyword_responses.items():
            if keyword in prompt.lower():
                return response

        # If no predefined keyword matches, grespond using the AI model
        response = self.chatbot(prompt, max_length=150, num_return_sequences=1)
        
        # Return the generated text
        return response[0]['generated_text'].strip()

    def chat(self):
        print("Hello! Please tell me about your situation.")
        while True:
            user_input = input("User: ")
            if user_input.strip() == '':
                print("Goodbye!")
                break

            # Generate a response based on user input
            if user_input:
                response = self.generate_response(user_input)
                print("Chatbot:", response)
            else:
                print("Please enter something.")

if __name__ == "__main__":
    # Create a Chatbot instance and start chatting
    bot = Chatbot()
    bot.chat()