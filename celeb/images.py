import os
import re
import urllib
import urlparse
import socket
import random
import string

import mechanize
import cookielib
import lxml.html
import PIL.Image
import PIL.ImageFile

TIMEOUT = 2
socket.setdefaulttimeout(TIMEOUT)


class ImageProcessor(object):
    '''This class handles the downloading and resizing of images.'''
    
    
    def __init__(self, path, min_size, resize, thumb_size, thumb_crop):
        self.path = path
        self.min_size = min_size
        self.resize = resize
        self.thumb_size = thumb_size
        self.thumb_crop = thumb_crop
        self.images = []
        
    def _generate_uuid(self, length=20):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for n in range(length))
    
    def _parse(self, urls, read_size=1024):
        '''This internal method parses a list of URLs, `urls`, using the PIL 
        ImageFile parser. Images are downloaded and read. The parser then 
        checks to make sure the image meets the minimum size requirement, 
        `min_size`.
        
        Images that meet the requirement are appended to a list and that list 
        is then returned.
        '''
        
        images = []
        for url in urls:
            url = urllib.unquote(url)
            image = urllib.urlopen(url)
            parser = PIL.ImageFile.Parser()
            #image = parser(image)
            while True:
                data = image.read(read_size)
                if not data:
                    break
                parser.feed(data)
                if parser.image and parser.image.size >= self.min_size:
                    images.append(url)
                    break
            image.close()
        return images
    
    def _save(self, images):
        '''This internal method takes a list of URLs, `images`, and saves them 
        to disk.
        
        Saved images are stored as a tuple, (image, path), and appended to a 
        list which is then returned.
        '''
        
        saved_images = []
        for image in images:
            image_ext = os.path.splitext(image)[-1]
            image_uuid = self._generate_uuid()
            new_name = image_uuid + image_ext
            save_path = os.path.join(self.path, new_name)
            try:
                urllib.urlretrieve(urllib.unquote(image), save_path)
                self.images.append(new_name)
                saved_images.append((new_name, save_path))
            except Exception:
                self.images.remove(new_name)
        return saved_images
    
    def _resize(self, images, suffix='-thumb'):
        '''This internal method takes a list containing two-element tuples, 
        `images`.
        
        Using PIL it then resizes the images and saves them as thumbnails.
        '''
        
        for image, path in images:
            try:
                open_image = PIL.Image.open(path)
                image_name, extension = os.path.splitext(image)
                thumb_image = image_name + suffix + extension
                thumb = os.path.join(self.path, thumb_image)
                open_image.thumbnail(self.resize, PIL.Image.ANTIALIAS)
                open_image = open_image.crop(self.thumb_crop)
                # open_image.thumbnail(self.thumb_size, PIL.Image.ANTIALIAS)
                open_image.save(thumb, 'JPEG')
                #self.images['thumb'].append(image_name + suffix)
            except IOError:
                pass
    
    def process(self, urls):
        images = self._parse(urls)
        images = self._save(images)
        self._resize(images)
        return self.images


class ImageFinder(object):
    '''This class finds links that are likely to be fullsize images.'''
    
    def _create_browser(self):
        browser = mechanize.Browser()
        
        # Cookie Jar
        cookie_jar = cookielib.LWPCookieJar()
        browser.set_cookiejar(cookie_jar)
        
        # Browser options
        browser.set_handle_equiv(True)
        #browser.set_handle_gzip(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        refresh_processor = mechanize._http.HTTPRefreshProcessor()
        browser.set_handle_refresh(refresh_processor, max_time=1)
        
        # User Agent
        browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        return browser
    
    def _parse_url(self, url, base):
        if url.startswith('//'):
            url = 'http:' + url 
        elif not url.startswith('http'):
            url = base + url
        return url
    
    def _find_links(self, url):
        '''This method takes a URL parameter, `url` and then uses the 
        mechanize browser to crawl a page, looking for images that are 
        wrapped with link tags, i.e. <a>.
        
        Having found such links, we then follow the links, appending these 
        URLs to our URL list.
        
        This URL list is then appended to the class attribute, `urls`.
        '''
        
        browser = self._create_browser()
        
        try:
            browser.open(url)
        except Exception, e:
            return 'Failed with exception: ' + str(e)
        
        links = browser.links(text='[IMG]')
        links = [link for link in links]
        links = range(len(links))
        
        urls = []
        for link in links:
            try:
                browser.follow_link(text='[IMG]', nr=link)
                urls.append(browser.geturl())
                browser.back()
            except Exception:
                pass
        return urls
    
    def find_images(self, url):
        '''This method takes a list of URLs, `urls`, and parses each URL with 
        lxml's HTML parser. 
        
        Duplicates are removed.
        
        Image URLs it finds are stored in the class attribute, `images`.
        '''
        
        images = []
        urls = self._find_links(url)
        for url in urls:
            try:
                url = lxml.html.parse(url)
                for image in url.findall('//img'):
                    src_url = image.attrib.get('src', '')
                    if re.findall('(?i)\.(?:jpe?g|png)$', src_url):
                        _url = urlparse.urlparse(image.base)[0]
                        _url += '://' + urlparse.urlparse(image.base)[1] + '/'
                        images.append(self._parse_url(src_url, _url))
                        images = list(set(images))
            except Exception:
                pass
        return images
