import sys, os, unittest, json, logging

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from bot.config import get_error_text


class test_config_get_error_text(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger().disabled = True

        #In production this is based on confile files
        os.environ["config_default"] = json.dumps({
            "error_texts" : {
                "one" : "default_error_one",
                "two" : "default_error_two",
            }
        })

        #The config for a guild with ID 3
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
        del os.environ['config_3']

    def test_get_error_text_default(self):
        self.assertEqual(get_error_text( "default", "one"), "default_error_one")
    
    def test_get_nonexistant_default(self):
        self.assertEqual(get_error_text( "default", "three"), "")

    def test_get_error_text_guild(self):
        self.assertEqual(get_error_text( "3", "one"), "guild_error_one")

    def test_get_nonexistant_guild(self):
        self.assertEqual(get_error_text( "3", "three"), "")

    def test_get_error_text_guild_fallback_to_default(self):
        self.assertEqual(get_error_text( "3", "two"), "default_error_two")

    def test_get_error_text_unknown_guild_no_fallback(self):
        self.assertEqual(get_error_text( "12", "three"), "")
    
    def test_get_error_text_unknown_guild_with_fallback(self):
        self.assertEqual(get_error_text( "12", "two"), "default_error_two")

    def test_can_get_nested_object(self):
        self.assertEqual(get_error_text("3", "nested", "layer_one"), {"layer_two":"guild_core"})
    
    def test_can_get_nested_string(self):
        self.assertEqual(get_error_text("3", "nested", "layer_one", "layer_two"), "guild_core")


if __name__ == '__main__':
    unittest.main()