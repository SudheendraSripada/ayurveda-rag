import unittest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from catalog_parser import parse_catalog_from_pdf, save_catalog_to_json, load_catalog_from_json, populate_database_catalog, CATALOG_JSON_PATH, DB_PATH  # noqa: E402

class TestCatalogExtraction(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        if os.path.exists(CATALOG_JSON_PATH):
            cls.books = load_catalog_from_json(CATALOG_JSON_PATH)
        else:
            cls.books = parse_catalog_from_pdf()
            save_catalog_to_json(cls.books, CATALOG_JSON_PATH)
        populate_database_catalog(cls.books, DB_PATH)
        
    def test_extracted_count_exact_3446(self):
        self.assertEqual(len(self.books), 3446, "Catalog should have exactly 3,446 books from 100 table pages")
        
    def test_ayurveda_treatises_identified(self):
        ayur_books = [b for b in self.books if b.get('is_ayurveda')]
        self.assertGreaterEqual(len(ayur_books), 100, "Should identify >= 100 authentic Ayurveda/health books")
        self.assertLessEqual(len(ayur_books), 130, "Should not exceed ~125 books (no false positives)")
        
        # Check classic texts are present
        titles_en = [b['title_english'].lower() for b in ayur_books]
        self.assertTrue(any("charaka" in t for t in titles_en), "Charaka Samhita must be present")
        self.assertTrue(any("ashtanga" in t for t in titles_en), "Ashtanga Hridaya must be present")
        self.assertTrue(any("kasyapa" in t for t in titles_en), "Kasyapa Samhita must be present")
        self.assertTrue(any("vanamulika" in t for t in titles_en), "Vanamulika Veda must be present")
        
    def test_zero_fake_download_titles(self):
        """Verify no books have titles corrupted by line wraps (e.g. '2 Download')."""
        corrupted = [b for b in self.books if "download" in b["title_telugu"].lower() or "download" in b["title_english"].lower()]
        self.assertEqual(len(corrupted), 0, f"Found corrupted books with 'Download' in title: {corrupted}")
        
    def test_no_non_ayurveda_false_positives(self):
        """Ensure non-Ayurvedic works in Upa Vedalu (economics, dance, arts) are NOT marked as Ayurveda."""
        titles_en_map = {b['title_english'].lower(): b for b in self.books}
        
        # Arthashastra / Economics
        self.assertIn("kowtilyuniardhasastram", titles_en_map)
        self.assertFalse(titles_en_map["kowtilyuniardhasastram"]["is_ayurveda"])
        self.assertIn("chanakyudu-ardhasastram", titles_en_map)
        self.assertFalse(titles_en_map["chanakyudu-ardhasastram"]["is_ayurveda"])
        self.assertIn("smallscaleindustries", titles_en_map)
        self.assertFalse(titles_en_map["smallscaleindustries"]["is_ayurveda"])
        
        # Gandharvaveda / Dance / Painting
        self.assertIn("natyasastram", titles_en_map)
        self.assertFalse(titles_en_map["natyasastram"]["is_ayurveda"])
        self.assertIn("paintingnerchukondi", titles_en_map)
        self.assertFalse(titles_en_map["paintingnerchukondi"]["is_ayurveda"])
        
    def test_all_links_valid_drive_urls(self):
        """Verify 100% of books have a valid FreeGurukul Google Drive link."""
        empty_links = [b for b in self.books if not b.get("url")]
        self.assertEqual(len(empty_links), 0, f"Found books without URL: {empty_links[:5]}")
        for b in self.books:
            self.assertTrue(b["url"].startswith("https://drive.google.com/"), f"Invalid URL for book #{b['id']}: {b['url']}")
            
    def test_canonical_categories_clean(self):
        """Verify canonical categories and zero books in 'ఇతరాలు'."""
        itaralu = [b for b in self.books if b["category"] == "ఇతరాలు"]
        self.assertEqual(len(itaralu), 0, f"Found books dumped in 'ఇతరాలు': {len(itaralu)}")
        
    def test_json_persisted_correctly(self):
        self.assertTrue(os.path.exists(CATALOG_JSON_PATH))
        loaded = load_catalog_from_json(CATALOG_JSON_PATH)
        self.assertEqual(len(loaded), 3446)
        
    def test_database_populated(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 3446)
        
    def test_book_fields_validity(self):
        for b in self.books[:100]:
            self.assertIn('id', b)
            self.assertIn('book_id', b)
            self.assertIn('category', b)
            self.assertIn('title_telugu', b)
            self.assertIn('title_english', b)
            self.assertIn('pages', b)
            self.assertIn('size_mb', b)
            self.assertIn('url', b)
            self.assertGreater(b['pages'], 0)
            self.assertTrue(b['url'].startswith('https://drive.google.com/'))

if __name__ == "__main__":
    unittest.main()
