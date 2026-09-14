import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import clean_text, chunk_text  # noqa: E402
from gemini_helper import SYSTEM_INSTRUCTION  # noqa: E402

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
        self.assertIn("STRICT DOMAIN RESTRICTIONS", SYSTEM_INSTRUCTION)
        self.assertIn("I am strictly authorized to provide health consultations and remedies based on Ayurvedic scriptures and reference books. I cannot assist with unrelated queries.", SYSTEM_INSTRUCTION)

    def test_query_expansion_precision(self):
        from rag_precision import expand_ayurvedic_query, calculate_precision_relevance_score, format_scriptural_context
        # Test digestion acidity clinical extraction
        res_acid = expand_ayurvedic_query("what is the Ayurvedic remedy for severe acid reflux and burning stomach?")
        self.assertIn("digestion_acidity", res_acid["matched_domains"])
        self.assertTrue(any("ఆమ్లపిత్తం" in t or "కడుపు" in t for t in res_acid["telugu_keywords"]))
        self.assertTrue(any("Amlapitta" in s for s in res_acid["sanskrit_keywords"]))
        self.assertTrue(any("Charaka" in tr for tr in res_acid["treatises"]))
        
        # Test respiratory cough entity extraction
        res_resp = expand_ayurvedic_query("how to treat dry cough and wheezing phlegm")
        self.assertIn("respiratory_cough", res_resp["matched_domains"])
        self.assertTrue(any("దగ్గు" in t for t in res_resp["telugu_keywords"]))
        self.assertTrue(any("Kasa" in s for s in res_resp["sanskrit_keywords"]))
        
        # Test joint pain arthritis entity extraction
        res_joint = expand_ayurvedic_query("knee joint pain and arthritis swelling")
        self.assertIn("joints_arthritis", res_joint["matched_domains"])
        self.assertTrue(any("Sandhivata" in s for s in res_joint["sanskrit_keywords"]))
        
        # Test precision relevance boost
        hit = {
            "score": 0.65,
            "is_ayurveda": True,
            "source_book": "CharakaSamhita-ChikitsaSthanamu",
            "text": "Charaka Amlapitta treatment with Yashtimadhu and Amalaki"
        }
        precision_score = calculate_precision_relevance_score(hit, res_acid)
        self.assertGreater(precision_score, 0.75)
        
        # Test scriptural context formatting
        passages = [
            {
                "source_book": "Charaka Samhita",
                "page_number": 44,
                "category": "ఉప వేదాలు",
                "download_url": "https://drive.google.com/sample",
                "text": "Charaka Chikitsa remedies"
            }
        ]
        context_block = format_scriptural_context(passages)
        self.assertIn("Source Treatise: Charaka Samhita", context_block)
        self.assertIn("Digital Archive URL: https://drive.google.com/sample", context_block)
        # Test word boundary precision: fluid retention should match edema_swelling, NOT fevers (flu)
        res_fluid = expand_ayurvedic_query("treatment for fluid retention in abdomen")
        self.assertNotIn("fevers_infections", res_fluid["matched_domains"])
        self.assertIn("edema_swelling", res_fluid["matched_domains"])
        self.assertTrue(any("Punarnava" in h for h in res_fluid["herbs"]))
        
        # Test headache migraine extraction
        res_head = expand_ayurvedic_query("severe migraine and throbbing temple headache")
        self.assertIn("headache_migraine", res_head["matched_domains"])
        self.assertTrue(any("Shirashoola" in s for s in res_head["sanskrit_keywords"]))

if __name__ == "__main__":
    print("Running Pipeline Unit Tests...")
    # Pass argv=[''] to avoid unittest attempting to parse command line args from the runner
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
