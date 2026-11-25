"""
Automated Test Suite for Interactive Musical Instrument Audio Demo & Sound Preview Feature
Tests:
1. Static asset verification (instrument_synth.js syntax and functions).
2. Detail page template markup & interactive note buttons.
3. Storefront catalog quick sound preview button markup.
4. CSS styling verification for audio components and animations.
5. Live HTTP rendering of detail and store pages with audio assets.
"""

import os
import unittest
from app import app

class TestAudioFeatureIntegrity(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_instrument_synth_js_integrity(self):
        """Verify instrument_synth.js exists and contains complete audio synthesis engine"""
        js_path = os.path.join("static", "js", "instrument_synth.js")
        self.assertTrue(os.path.exists(js_path), "instrument_synth.js file must exist")

        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check core components
        self.assertIn("SoundCraftSynth", content)
        self.assertIn("AudioContext", content)
        self.assertIn("playTone", content)
        self.assertIn("playDemo", content)
        self.assertIn("stopDemo", content)
        self.assertIn("playSingleNote", content)
        self.assertIn("previewCardSound", content)

        # Check instrument family synthesis presets
        self.assertIn("sitar", content)
        self.assertIn("piano", content)
        self.assertIn("bowed", content)
        self.assertIn("woodwind", content)
        self.assertIn("brass", content)
        self.assertIn("percussion", content)
        self.assertIn("plucked", content)

        # Check notes dictionary
        self.assertIn("'C4': 261.63", content)
        self.assertIn("'A4': 440.00", content)

    def test_02_detail_template_sound_card(self):
        """Verify instrument_detail.html contains interactive sound demo card and notes"""
        tmpl_path = os.path.join("templates", "customer", "instrument_detail.html")
        with open(tmpl_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("detail-sound-demo-card", content)
        self.assertIn("Instrument Sound Demo", content)
        self.assertIn("btn-play-demo", content)
        self.assertIn("SoundCraftSynth.playDemo", content)
        self.assertIn("sound-visualizer", content)
        self.assertIn("interactive-keys-section", content)

        # Check all 8 note buttons
        for swara in ["Sa", "Ri", "Ga", "Ma", "Pa", "Dha", "Ni", "Sȧ"]:
            self.assertIn(f">{swara}<", content)

        # Check script inclusion
        self.assertIn("instrument_synth.js", content)

    def test_03_storefront_card_preview_markup(self):
        """Verify store.html contains audio preview button on catalog cards"""
        tmpl_path = os.path.join("templates", "customer", "store.html")
        with open(tmpl_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("btn-card-audio-preview", content)
        self.assertIn("SoundCraftSynth.previewCardSound", content)
        self.assertIn("instrument_synth.js", content)

    def test_04_css_styles_integrity(self):
        """Verify style.css contains necessary audio demo and visualizer classes"""
        css_path = os.path.join("static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".detail-sound-demo-card", content)
        self.assertIn(".btn-play-demo", content)
        self.assertIn(".sound-visualizer", content)
        self.assertIn("@keyframes soundBounce", content)
        self.assertIn(".btn-note-key", content)
        self.assertIn(".btn-card-audio-preview", content)

    def test_05_live_http_rendering(self):
        """Verify live HTTP endpoints deliver the audio player markup cleanly"""
        # Test store catalog
        store_res = self.client.get('/store')
        self.assertEqual(store_res.status_code, 200)
        self.assertIn(b"btn-card-audio-preview", store_res.data)
        self.assertIn(b"instrument_synth.js", store_res.data)

        # Test instrument detail view
        detail_res = self.client.get('/customer/instrument/INS001')
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn(b"detail-sound-demo-card", detail_res.data)
        self.assertIn(b"btn-play-demo", detail_res.data)
        self.assertIn(b"sound-visualizer", detail_res.data)
        self.assertIn(b"btn-note-key", detail_res.data)
        self.assertIn(b"instrument_synth.js", detail_res.data)


if __name__ == '__main__':
    unittest.main()
