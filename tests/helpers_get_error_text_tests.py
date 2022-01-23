import sys, os, unittest, json, logging

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import bot.helpers as helpers


class test_helpers_get_error_text(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger().disabled = True

        os.environ["config_default"] = json.dumps({
            "error_texts" : {
                "one" : "default_error_one",
                "two" : "default_error_two",
            }
        })

        os.environ["config_3"] = json.dumps({
            "error_texts" : {
                "one" : "guild_error_one",
                "nested" : {
                    "layer_one" : {
                        "layer_two" : "guild_core"
                    }
                }
            }
	    })
        
    @classmethod
    def tearDownClass(cls):
        logging.getLogger().disabled = False
        del os.environ['config_default']

    def test_get_error_text_default(self):
        self.assertEqual(helpers.get_error_text( "default", "one"), "default_error_one")
    
    def test_get_nonexistant_default(self):
        self.assertEqual(helpers.get_error_text( "default", "three"), "")

    def test_get_error_text_guild(self):
        self.assertEqual(helpers.get_error_text( "3", "one"), "guild_error_one")

    def test_get_nonexistant_guild(self):
        self.assertEqual(helpers.get_error_text( "3", "three"), "")

    def test_get_error_text_guild_fallback_to_default(self):
        self.assertEqual(helpers.get_error_text( "3", "two"), "default_error_two")

    def test_get_error_text_unknown_guild_no_fallback(self):
        self.assertEqual(helpers.get_error_text( "12", "three"), "")
    
    def test_get_error_text_unknown_guild_with_fallback(self):
        self.assertEqual(helpers.get_error_text( "12", "two"), "default_error_two")


if __name__ == '__main__':
    unittest.main()