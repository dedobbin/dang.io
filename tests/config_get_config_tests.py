import sys, os, unittest, json, logging

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from bot.config import get_config


class test_config_get_config(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger().disabled = True

        #In production this is based on confile files
        os.environ["config_default"] = json.dumps({
            "test" : "default_config",
	        "fallback_test" : "fallback_value",
            "some_text" : "this is some text",
	        "nested_test" : {
                "layer_one" : {
                    "layer_two" : "default_core",
                },
            },
            "second_nest" : {
                "layer_one" : "second_default_core"
            }
        })

        #The config for a guild with ID 3
        os.environ["config_3"] = json.dumps({
            "test" : "guild_config",
	        "nested_test" : {
                "layer_one" : {
                    "layer_two" : "guild_core"
                }
            },
            "second_nest" : {

            }
	    })
        
    @classmethod
    def tearDownClass(cls):
        logging.getLogger().disabled = False
        del os.environ['config_default']
        del os.environ['config_3']

    def test_nonexistant_config_key_default(self):
        self.assertEqual(get_config( "default", "nonexistant"), "")

    def test_existant_config_key_default(self):
        self.assertEqual(get_config( "default", "test"), "default_config")

    def test_nonexistant_config_key_guild(self):
        self.assertEqual(get_config( "3", "nonexistant"), "")

    def test_guild_gets_their_own_config_values(self):
        self.assertEqual(get_config("3","test"), "guild_config")

    def test_guild_gets_default_for_nonexisting_key(self):
        self.assertEqual(get_config("3", "fallback_test"), "fallback_value")
    
    def test_unknown_guild_get_gets_default(self):
        self.assertEqual(get_config("12", "fallback_test"), "fallback_value")
    
    def test_unknown_guild_nonexistant_key(self):
        self.assertEqual(get_config("12", "nonexistant"), "")
    
    def test_nested_data_guild(self):
        self.assertEqual(get_config("3", "nested_test", "layer_one"), {"layer_two" : "guild_core"})
        self.assertEqual(get_config("3", "nested_test", "layer_one", "layer_two"), "guild_core")

    def test_nested_data_default(self):
        self.assertEqual(get_config("default", "nested_test", "layer_one"), {"layer_two" : "default_core"})
        self.assertEqual(get_config("default", "nested_test", "layer_one", "layer_two"), "default_core")

    def test_nested_data_unknown_guild(self):
        self.assertEqual(get_config("12", "nested_test", "layer_one"), {"layer_two" : "default_core"})
        self.assertEqual(get_config("12", "nested_test", "layer_one", "layer_two"), "default_core")
    
    def test_nested_data_guild_fallback(self):
        self.assertEqual(get_config("3", "second_nest", "layer_one"), "second_default_core")

if __name__ == '__main__':
    unittest.main()