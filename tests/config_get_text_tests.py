import sys, os, unittest, json, logging

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from bot.config import get_text


class test_config_get_texts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger().disabled = True

        #In production this is based on confile files
        os.environ["config_default"] = json.dumps({
            "texts" : {
                "one" : "default_text_one",
                "two" : "default_text_two",
            }
        })

        #The config for a guild with ID 3
        os.environ["config_3"] = json.dumps({
            "texts" : {
                "one" : "guild_text_one",
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

    def test_get_text_default(self):
        self.assertEqual(get_text( "default", "one"), "default_text_one")
    
    def test_get_nonexistant_default(self):
        self.assertEqual(get_text( "default", "three"), "")

    def test_get_text_guild(self):
        self.assertEqual(get_text( "3", "one"), "guild_text_one")

    def test_get_nonexistant_guild(self):
        self.assertEqual(get_text( "3", "three"), "")

    def test_get_text_guild_fallback_to_default(self):
        self.assertEqual(get_text( "3", "two"), "default_text_two")

    def test_get_text_unknown_guild_no_fallback(self):
        self.assertEqual(get_text( "12", "three"), "")
    
    def test_get_text_unknown_guild_with_fallback(self):
        self.assertEqual(get_text( "12", "two"), "default_text_two")

    def test_can_get_nested_object(self):
        self.assertEqual(get_text("3", "nested", "layer_one"), {"layer_two":"guild_core"})
    
    def test_can_get_nested_string(self):
        self.assertEqual(get_text("3", "nested", "layer_one", "layer_two"), "guild_core")

if __name__ == '__main__':
    unittest.main()