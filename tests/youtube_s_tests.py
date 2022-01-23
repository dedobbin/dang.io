import sys, os, unittest, logging
from unittest.mock import MagicMock, patch, ANY

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from bot.youtube_s import Youtube_S


class test_helpers_get_texts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger().disabled = True
        
    @classmethod
    def tearDownClass(cls):
        logging.getLogger().disabled = False

    def test_constructor_calls_create_web_driver(self):
        with patch.object(Youtube_S, 'create_web_driver', return_value=3) as mock_method:
            Youtube_S()
            mock_method.assert_called_once()

    def test_obscure_videos_have_no_more_than_100_views(self):
        with patch.object(Youtube_S, 'create_web_driver', return_value=3) as mock_method:
            s = Youtube_S()
            
        with patch.object(Youtube_S, 'get_videos', return_value=[
            {'views': 100000, 'live': False, 'url': ''},
            {'views': 24, 'live': False, 'url': ''},
            {'views': 500, 'live': False, 'url': ''},
        ]) as mock_method:
            videos = s.get_obscure_videos()
            
            mock_method.assert_called_once()

        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]['views'], 24)

    def test_getting_obscure_videos_passes_correct_args_to_get_videos(self):
        with patch.object(Youtube_S, 'create_web_driver', return_value=3) as mock_method:
            s = Youtube_S()

        with patch.object(Youtube_S, 'get_videos', return_value=[
            {'views': 100000, 'live': False, 'url': ''},
        ]) as mock_method:
            s.get_obscure_videos('the beatles')
            mock_method.assert_called_with(s.param_last_hour)

            s.get_obscure_videos('the beatles')
            mock_method.assert_called_with({**s.param_last_hour, 'search_query': 'the beatles'})



if __name__ == '__main__':
    unittest.main()