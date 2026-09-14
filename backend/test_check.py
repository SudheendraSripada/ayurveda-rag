import unittest
import os
from pinecone_helper import resolve_pinecone_api_key, get_index_stats, search_index
from main import retrieve_ayurvedic_context
from rag_precision import expand_ayurvedic_query

class TestPineconeRAGIntegration(unittest.TestCase):
    
    def test_pinecone_key_resolved(self):
        key = resolve_pinecone_api_key()
        self.assertTrue(bool(key), "Pinecone API key must resolve from env or config")
        self.assertTrue(key.startswith("pcsk_"), "Pinecone API key should start with pcsk_")
        
    def test_pinecone_index_stats(self):
        stats = get_index_stats(index_name="ayurveda-index")
        self.assertTrue(stats.get("exists"), "Index ayurveda-index should exist")
        self.assertGreaterEqual(stats.get("total_vector_count", 0), 3400, "Should have over 3400 vectors indexed")
        
    def test_retrieve_ayurvedic_context_precision(self):
        # Query for classic treatises
        passages = retrieve_ayurvedic_context("What are the classic remedies in Charaka Samhita for fevers and digestion?", rerank=False)
        self.assertGreater(len(passages), 0, "Should retrieve relevant scripture passages")
        
        # Check metadata fields
        first = passages[0]
        self.assertIn("source_book", first)
        self.assertIn("category", first)
        self.assertIn("download_url", first)
        self.assertTrue(first["download_url"].startswith("http") or first["download_url"] == "")
        
    def test_query_expansion_telugu(self):
        analysis = expand_ayurvedic_query("మోకాళ్ల నొప్పులు మరియు వాతం నివారణ")
        self.assertIn("joints_arthritis", analysis["matched_domains"])
        self.assertTrue(any("Sandhivata" in s for s in analysis["sanskrit_keywords"]))

    def test_filtered_retrieval_excludes_non_ayurveda(self):
        # Query for dry cough and throat irritation
        passages = retrieve_ayurvedic_context("What is the classical remedy for persistent dry cough and phlegm?", rerank=False)
        self.assertGreater(len(passages), 0)
        for p in passages:
            self.assertTrue(p.get("is_ayurveda", False), f"Retrieved non-Ayurvedic passage in clinical query: {p.get('source_book')}")

if __name__ == "__main__":
    unittest.main()
