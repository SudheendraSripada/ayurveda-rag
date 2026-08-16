import os
import unittest
from pdf_parser import clean_text, chunk_text
from pinecone_helper import get_pinecone_client
from gemini_helper import SYSTEM_INSTRUCTION

class TestAyurvedaRAGPipeline(unittest.TestCase):
    
    def test_clean_text(self):
        raw_text = "This   is   a \n\n\ntest \r\nwith multiple   whitespaces."
        cleaned = clean_text(raw_text)
        self.assertIn("This is a\n\ntest\nwith multiple whitespaces.", cleaned)
        
    def test_chunk_text(self):
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks:
            self.assertTrue(len(chunk) <= 100) # Should be within soft bounds

    def test_guardrails_instruction(self):
        self.assertIn("STRICTOR DOMAIN GUARDRAILS", SYSTEM_INSTRUCTION)
        self.assertIn("I am strictly authorized to provide health consultations and remedies based on Ayurvedic scriptures and reference books. I cannot assist with unrelated queries.", SYSTEM_INSTRUCTION)

if __name__ == "__main__":
    print("Running Pipeline Unit Tests...")
    # Pass argv=[''] to avoid unittest attempting to parse command line args from the runner
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
