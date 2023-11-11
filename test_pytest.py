import pytest
from unittest.mock import patch, MagicMock
from web import google_search, get_im, add_img, get_end, scroll, download_image
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import requests
from io import BytesIO
from PIL import Image


@pytest.fixture
def mock_webdriver():
    # This will be your mock webdriver for use in tests.
    class WebDriverMock:
        current_url = "http://example.com"  # Add a default URL or mock behavior

        def __init__(self):
            self.execute_script = MagicMock()

        def get(self, url):
            pass


        def execute_script(self, script):
            pass

        def quit(self):
            pass


        def execute_script(self, script):
            pass

        def find_elements(self, by, value):
            mock_element = MagicMock()
            # Set up the mock element to return the image URL when get_attribute('src') is called
            mock_element.get_attribute.return_value = 'http://example.com/image1.png'
            return [mock_element]

    return WebDriverMock()

@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        mock_content = MagicMock(content=b"image content")
        mock_get.return_value = mock_content
        yield mock_get

@pytest.fixture
def mock_requests_get_fail():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Invalid URL")
        yield mock_get


# Test google_search function

def test_google_search(mock_webdriver):
    with patch('sel_scrape.WebDriverWait') as mock_wait:
        mock_element = MagicMock()
        mock_wait.return_value.until.return_value = mock_element
        google_search(mock_webdriver, "search_term")
        mock_element.send_keys.assert_called_once_with("search_term" + Keys.RETURN)


# Test get_im function
def test_get_im(mock_webdriver):
    with patch('sel_scrape.get_end') as mock_get_end, \
         patch('sel_scrape.add_img') as mock_add_img, \
         patch('sel_scrape.scroll') as mock_scroll:

        mock_add_img.return_value = ['http://example.com/image1.png']
        mock_get_end.return_value = None
        mock_scroll.return_value = None

        image_urls = get_im(mock_webdriver, 2, 'http://example.com')
        assert len(image_urls) > 0
        assert 'http://example.com/image1.png' in image_urls


# Test add_img function
def test_add_img(mock_webdriver):
    mock_img = MagicMock()
    mock_img.get_attribute.return_value = 'http://example.com/image1.png'
    mock_webdriver.find_elements = MagicMock(return_value=[mock_img])

    thumbnails = [MagicMock()]
    image_urls = add_img(mock_webdriver, thumbnails)  # Update to pass two arguments
    assert 'http://example.com/image1.png' in image_urls




# Test scroll function
def test_scroll(mock_webdriver):
    mock_webdriver.execute_script = MagicMock()
    with patch('time.sleep') as mock_sleep:
        scroll(mock_webdriver)
        mock_webdriver.execute_script.assert_called_once_with('window.scrollTo(0,document.body.scrollHeight);')
        mock_sleep.assert_called_once()


# Test download_image function
def test_download_successful(mock_requests_get, tmpdir):
    path = tmpdir.strpath + "/"
    url = "http://testurl.com/testimage.png"
    filename = "testimage.png"
    download_image(path, url, filename, verbose=False)
    assert (tmpdir / filename).check(file=1)




def test_google_search_click_images_exception(mock_webdriver):
    with patch('sel_scrape.WebDriverWait') as mock_wait:
        mock_wait.return_value.until.side_effect = WebDriverException('Click Images failed')
        with pytest.raises(WebDriverException):
            google_search(mock_webdriver, "search_term")


def test_webdriver_get(mock_webdriver):
    mock_webdriver.get("http://example.com")
    assert mock_webdriver.current_url == "http://example.com"

def test_find_elements_empty(mock_webdriver):
    mock_webdriver.find_elements = MagicMock(return_value=[])
    image_urls = get_im(mock_webdriver, 2, 'http://example.com')
    assert len(image_urls) == 0


def test_execute_script_argument(mock_webdriver):
    script = 'return window.innerHeight;'
    mock_webdriver.execute_script(script)
    mock_webdriver.execute_script.assert_called_with(script)


def test_get_im_no_thumbnails(mock_webdriver):
    mock_webdriver.find_elements = MagicMock(return_value=[])
    image_urls = get_im(mock_webdriver, 2, 'http://example.com')
    assert image_urls == set()



# Test get_im function to handle no new images after scrolling and clicking "Show more results"
def test_get_im_no_new_images_after_show_more(mock_webdriver):
    mock_webdriver.find_elements = MagicMock(return_value=[MagicMock()])
    # Assume add_img and get_end are patched to simulate no new images after "Show more results"
    with patch('sel_scrape.add_img') as mock_add_img, \
         patch('sel_scrape.get_end') as mock_get_end:
        mock_add_img.return_value = set()
        mock_get_end.return_value = None
        image_urls = get_im(mock_webdriver, 2, 'http://example.com')
        assert len(image_urls) == 0



# Test click on 'Show more results' button
def test_click_show_more_results_present(mock_webdriver):
    with patch('sel_scrape.WebDriverWait') as mock_wait:
        # Simulate the button being found and clickable
        mock_button = MagicMock()
        mock_wait.return_value.until.return_value = mock_button
        get_end(mock_webdriver)
        # Assert the button was clicked
        mock_button.click.assert_called_once()



# Test the handling when no more images are found after several scrolls
def test_no_more_images_after_scrolls(mock_webdriver):
    with patch('sel_scrape.add_img') as mock_add_img, \
            patch('sel_scrape.scroll') as mock_scroll, \
            patch('sel_scrape.get_end') as mock_get_end:
        
        mock_add_img.return_value = set()  # Simulate no more images being added
        mock_get_end.return_value = None   # Simulate no 'Show more results' button
        mock_scroll.return_value = None    # Simulate scrolls without new images
        
        # Call the function with the mocked conditions
        image_urls = get_im(mock_webdriver, 2, 'http://example.com')
        
        # Assert that the image_urls is empty since no new images were found
        assert len(image_urls) == 0

def test_download_image_verbose_print(capfd, mock_requests_get, tmpdir):
    path = tmpdir.strpath + "/"
    url = "http://testurl.com/testimage.png"
    filename = "testimage.png"
    
    # Mock the response content to be an image file
    image_content = BytesIO()
    Image.new('RGB', (60, 30), color = 'red').save(image_content, format='PNG')
    image_content.seek(0)
    mock_requests_get.return_value.content = image_content.read()
    
    # Run the download function with verbose=True
    download_image(path, url, filename, verbose=True)
    
    # Capture the print output
    out, err = capfd.readouterr()
    
    # Assert that the expected message was printed
    assert 'The image: ' in out
    assert 'downloaded successful at ' in out


def test_add_img_exception(mock_webdriver):
    mock_img = MagicMock()
    
    # Simulate an exception when img.click() is called
    mock_img.click.side_effect = Exception("Click failed")
    
    thumbnails = [mock_img]
    image_urls = add_img(mock_webdriver, thumbnails)
    
    # Assert that the exception was caught and the function continued
    assert len(image_urls) == 0

def test_add_img_with_duplicate_url(mock_webdriver):
    mock_img1 = MagicMock()
    mock_img1.get_attribute.return_value = 'http://example.com/image1.png'

    mock_img2 = MagicMock()
    mock_img2.get_attribute.return_value = 'http://example.com/image1.png'

    thumbnails = [mock_img1, mock_img2]
    image_urls = add_img(mock_webdriver, thumbnails)

    # Assert that only one URL is added, as per the original behavior
    assert len(image_urls) == 1
    assert 'http://example.com/image1.png' in image_urls


def test_download_image_failure_print_statement(capfd, mock_requests_get_fail, tmpdir):
    path = tmpdir.strpath + "/"
    url = "http://testurl.com/testimage.png"
    filename = "testimage.png"
    
    # Call the download_image function which is expected to fail
    download_image(path, url, filename, verbose=True)
    
    # Capture the stdout and stderr
    out, err = capfd.readouterr()
    
    # Check if the expected failure message is in the output
    assert "download failed due to:" in out



