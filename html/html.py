"""This module provides an HTML parsing class.

    Packages(s) required:
    - cgi
    - contextlib
    - datetime
    - HTMLParser
    - logging
    - requests
    - time
    - urllib2

    To-do:
    - Implement/fix case-insensitivity on find_first/next_tag
    - Add get_tag(text, tag_name, starting_index)
    - Add get_nearest_match()
    - Add strip_tags()

"""

# Imports
import cgi
import contextlib
import datetime
import HTMLParser
import logging
import requests
import time
import urllib2
#from __future__ import with_statement # required if using Python 2.5

from atom import Tag


class Error(Exception):
    """General base exception class for this module."""
    pass


class HTML(HTMLParser.HTMLParser):
    """HTML parsing class.

    Attributes:
        requests_per_minute: The maximum number of requests allowed per minute.
        minimum_time_between_requests: The minimum time required between
            requests.

    """
    # Public member variables
    requests_per_minute = 120
    minimum_time_between_requests = 0

    # Private member variables
    _parsed_data = None
    _root = None
    _current_tag = None
    _number_of_tags = None
    _last_request_time = None  # date/time of last HTTP request
    _rate_limit_counter_time = None  # date/time for rate limit periods
    _rate_limit_count = 0  # number of HTTP requests during this rate period

    # Private member objects
    _logger = None

    def __init__(self, log_handler=None):
        """Create and initialize the HTML parser.

        Prepare the parent class for processing, reset the root Tag, tag
        counter, and rate limiting.

        Args:
            log_handler: The log handler to use instead of the default.

        """
        self._logger = logging.getLogger(__name__)
        handler = None
        if log_handler:
            handler = log_handler
        else:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s:'
                                          '%(name)s:%(message)s')
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        self._parsed_data = []
        self._root = Tag(name='root', children=[])
        self._current_tag = self._root
        self._number_of_tags = 0
        HTMLParser.HTMLParser.__init__(self)
        self._rate_limit_counter_time = datetime.datetime.now()
        self._logger.debug("rate_limit_counter_time = %i",
                           self._rate_limit_counter_time)

    def get_url(self, url, form_data=None):
        """Get data from a url.

        Args:
            form_data: A dictionary containing name/value pairs of form data.
            url: The URL to get data from.

        Returns:
            The data from the URL as a string.

        """
        data = None
        # If a url is specified, open it
        if url and len(url) > 0:
            try:
                if form_data:
                    self._logger.debug("Form data: %s", str(form_data))
                    with contextlib.closing(requests.post(url,
                                                      data=form_data)) as req:
                        data = req.text
                else:
                    with contextlib.closing(urllib2.urlopen(url)) as html_file:
                        data = html_file.read()
                self._logger.debug("URL contents: %s", str(data))
            except urllib2.URLError as excep:
                raise Error("URL error opening the url: %s", str(excep))
            except requests.ConnectionError as excep:
                raise Error("Connection error opening the url: %s", str(excep))
            except requests.HTTPError as excep:
                raise Error("HTTP error opening the url: %s", str(excep))
            except requests.Timeout as excep:
                raise Error("Timeout error opening the url: %s", str(excep))
            except requests.TooManyRedirects as excep:
                raise Error("Too many redirects error opening the url: %s",
                            str(excep))
        return data

    def parse_file(self, file_name):
        """Parse an HTML file.

        Args:
            file_name: The HTML file to parse.

        Returns:
            True if the file was parsed successfully.

        """
        html_file = None
        # If a file is specified, open it
        if file_name and len(file_name) > 0:
            self._logger.info("Parsing the file: %s", str(file_name))
            try:
                # Open the file
                with open(file_name) as html_file:
                    # Read the markup text
                    data = html_file.read()
                    self._logger.debug("File contents: %s", str(data))
            except IOError as excep:
                raise Error("IOError opening the file: %s", str(excep))

            # Parse the markup text
            return self.parse(data)
        else:
            self._logger.error("No file specified")
        return False

    def parse_url(self, url, wait_for_rate_limiting=True):
        """Download and parse a URL.

        Args:
            url: The URL to parse.
            wait_for_rate_limiting: True to block for rating limiting.

        Returns:
            True if the URL was parsed successfully.

        """
        # If a url is specified, open it
        if url and len(url) > 0:
            self._logger.info("Parsing the url: %s", str(url))

            # Check rate limiting
            if not self._check_rate_limiting(wait_for_rate_limiting):
                return False

            # Store the time when the request is made
            current_time = datetime.datetime.now()
            self._logger.debug("current_time: %i", current_time)

            data = self.get_url(url)

            # Update rate limit info
            self._update_rate_limiting(current_time)

            # Parse the markup text
            return self.parse(data)
        else:
            self._logger.error("No URL specified")
        return False

    def parse_url_with_post_form(self, url, form_data,
                                 wait_for_rate_limiting=True):
        """Download and parse a URL using a POST form.

        Args:
            url: The URL to parse.
            form_data: A dictionary containing name/value pairs of form data.
            wait_for_rate_limiting: True to block for rating limiting.

        Returns:
            True if the URL was parsed successfully.

        """
        # If a url is specified, open it
        if url and len(url) > 0 and form_data:
            self._logger.info("Parsing the url with POST form: %s", str(url))
            self._logger.debug("POST data: %s", str(form_data))

            # Check rate limiting
            if not self._check_rate_limiting(wait_for_rate_limiting):
                return False

            # Store the time when the request is made
            current_time = datetime.datetime.now()
            self._logger.debug("current_time: %i", current_time)

            data = self.get_url(url, form_data)

            # Update rate limit info
            self._update_rate_limiting(current_time)

            # Parse the markup text
            return self.parse(data)
        else:
            self._logger.error("No URL or form data specified")
        return False

    def _check_rate_limiting(self, wait_for_rate_limiting=True):
        """Check for rate limiting.

        Check the rate limiting and optionally pause if required to avoid
        exceeding the rate limit.

        Args:
            wait_for_rate_limiting: True to block for rating limiting.

        Returns:
            True if rate limit was handled properly.

        """
        # Check rate limiting: time between requests
        self._logger.info("Checking rate limiting")
        self._logger.debug("wait_for_rate_limiting = %s",
                           str(wait_for_rate_limiting))
        current_time = datetime.datetime.now()
        self._logger.debug("current_time: %i", current_time)
        if (self._last_request_time and
            ((current_time - self._last_request_time) <
            datetime.timedelta(seconds=self.minimum_time_between_requests))):
            self._logger.debug("Rate limit triggered, time delta: %i, minimum"
                               " time between requests: %i",
                               (current_time - self._last_request_time),
                               self.minimum_time_between_requests)
            if wait_for_rate_limiting:
                self._logger.debug("Waiting for rate limiting")
                time.sleep(self.minimum_time_between_requests)
            else:
                self._logger.debug("Not waiting for rate limiting, aborting")
                return False

        # Check rate limiting: requests per minute
        current_time = datetime.datetime.now()      # Get current time
        if self._rate_limit_count >= self.requests_per_minute:
            self._logger.debug("Rate limit triggered, rate limit count: %i, "
                               "requests per minute: %i",
                               self._rate_limit_count, self.requests_per_minute)
            if wait_for_rate_limiting:
                self._logger.debug("Waiting for rate limiting")
                rate_delay = (60 -
                              (current_time -
                              self._rate_limit_counter_time).seconds)
                if rate_delay > 0:
                    time.sleep(rate_delay)
                else:
                    time.sleep(self.minimum_time_between_requests)
            else:
                self._logger.debug("Not waiting for rate limiting, aborting")
                return False

        # Rate limiting not needed, or it was and we waited the required time
        return True

    def _update_rate_limiting(self, current_time):
        """Update rate limit data.

        Args:
            current_time: The time of the current request.

        """
        # Update rate limit info
        self._logger.info("Updating rate limiting")
        self._last_request_time = datetime.datetime.now()
        self._logger.debug("last_request_time: %i", self._last_request_time)
        if ((current_time - self._rate_limit_counter_time) >
            datetime.timedelta(minutes=1)):
            self._logger.debug("Reset rate limiting")
            self._rate_limit_counter_time = self._last_request_time
            self._logger.debug("rate_limit_counter_time: %i",
                               self._rate_limit_counter_time)
            self._rate_limit_count = 0
        self._rate_limit_count += 1
        self._logger.debug("rate_limit_count: %i", self._rate_limit_count)

    def parse(self, markup_text):
        """Parse HTML markup.

        Args:
            markup_text: The HTML markup text to parse.

        Returns:
            True if the markup was parsed successfully.

        """
        self._logger.info("Parsing HTML markup")
        # Start with the root of the document
        self._parsed_data = []
        self._root = Tag(name='root', children=[])
        self._current_tag = self._root
        self._number_of_tags = 0
        self.reset()

        # Fix any issues before we call the parser
        if markup_text:
            markup_text = markup_text.replace('</>', '</a>')
            self._logger.debug("Replaced </> with </a>")
            try:
                # Feed our data to the parser
                self.feed(markup_text)
            except HTMLParser.HTMLParseError as excep:
                raise Error("Error parsing HTML: %s", str(excep))
        # Store the root tag to the list of HTML tags
        self._store_tag(self._root)
        self._number_of_tags = len(self._parsed_data)
        self._logger.debug("finished parsing. Position "
                           "- %s", str(self.getpos()))
        self._logger.debug("%s tags processed", str(self._number_of_tags))

        return True

    def _store_tag(self, tag):
        """Store the current tag.

        Args:
            tag: The Tag object to store in the flat list.

        """
        if tag:
            self._logger.info("Storing tag")
            # Store the tag data to the list of tags
            self._parsed_data.append([tag.name, tag.attributes, tag.data])
            self._logger.debug("Adding tag: [%s, %s, %s]", str(tag.name),
                               str(tag.attributes), str(tag.data))
            # If the tag has children, recursively call this function to
            # store them as well
            if tag.children and len(tag.children) > 0:
                self._logger.debug("Adding %i children", len(tag.children))
                for i in range(0, len(tag.children)):
                    self._store_tag(tag.children[i])
        else:
            self._logger.error("No tag specified")

    def handle_starttag(self, tag, attrs):
        """Handle the start of an HTML tag.

        Event handler for when the start of a tag is encountered.

        Args:
            tag: The HTML tag.
            attrs: A list of the tag's attributes.

        """
        self._logger.debug("start tag - %s / %s", tag, str(attrs))
        new_tag = Tag(name=tag, attributes=attrs, parent=self._current_tag,
                      data='')
        self._logger.debug("parent tag: %s", str(self._current_tag.name))
        if not self._current_tag.children:
            self._current_tag.children = []
        self._current_tag.children.append(new_tag)
        self._current_tag = new_tag

    def handle_endtag(self, tag):
        """Handle the end of an HTML tag.

        Event handler for when the end of a tag is encountered.

        Args:
            tag: The HTML tag.

        """
        self._logger.debug("end tag - %s", tag)
        self._current_tag.data = ''.join(self._current_tag.string_concat_list)
        if tag == 'em':
            self._current_tag.parent.string_concat_list.append(
                                                        self._current_tag.data)
        self._current_tag = self._current_tag.parent

    def handle_startendtag(self, tag, attrs):
        """Handle a start/end HTML tag.

        Event handler for when a tag that is both the start and end of a tag
        is encountered.

        Args:
            tag: The HTML tag.
            attrs: A list of the tag's attributes.

        """
        self._logger.debug("start/end tag - %s / %s", tag, str(attrs))
        if tag == 'br':
            self._current_tag.string_concat_list.append(" ")
        new_tag = Tag(name=tag, attributes=attrs, parent=self._current_tag)
        if not self._current_tag.children:
            self._current_tag.children = []
        self._current_tag.children.append(new_tag)

    def handle_data(self, data):
        """Handle the data of an HTML tag.

        Event handler for when the content of a tag is encountered.

        Args:
            data: The tag's data.

        """
        self._logger.debug("data - %s", data)
        if data:
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            if len(data) > 0:
                if not self._current_tag.data:
                    self._current_tag.data = ""
                self._current_tag.string_concat_list.append(data)

    def handle_comment(self, data):
        """Handle a comment.

        Event handler for when a comment is encountered.

        Args:
            data: The comment.

        """
        self._logger.debug("comment - %s", data)
        if data:
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            if len(data) > 0:
                new_tag = Tag(name='comment', parent=self._current_tag,
                              data=data)
                if not self._current_tag.children:
                    self._current_tag.children = []
                self._current_tag.children.append(new_tag)

    def handle_decl(self, decl):
        """Handle a declaration.

        Event handler for when a declaration is encountered.

        Args:
            decl: The declaration.

        """
        self._logger.debug("declaration - %s", decl)
        if decl:
            decl = decl.replace("\n", "")
            decl = decl.replace("\r", "")
            if len(decl) > 0:
                new_tag = Tag(name='declaration', parent=self._current_tag,
                              data=decl)
                if not self._current_tag.children:
                    self._current_tag.children = []
                self._current_tag.children.append(new_tag)

    def unknown_decl(self, data):
        """Handle an unknown declaration.

        Event handler for when an unknown declaration is encountered.

        Args:
            data: The declaration.

        """
        self._logger.debug("declaration - %s", data)
        if data:
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            if len(data) > 0:
                new_tag = Tag(name='unknown_declaration',
                              parent=self._current_tag, data=data)
                if not self._current_tag.children:
                    self._current_tag.children = []
                self._current_tag.children.append(new_tag)

    def find_first_tag(self, tag_type, tag_attributes=None, tag_data=None):
        """Find the first matching tag.

        Find the first matching tag using tag type attributes, or content.

        Args:
            tag_type: The type of tag to search for.
            tag_attributes: The tag attributes to search for.
            tag_data: The tag data to search for.

        Returns:
            The index in the flat list of the first matching tag, or -1.

        """
        return self.find_next_tag(tag_type, tag_attributes, tag_data)

    def find_next_tag(self, tag_type, tag_attributes=None, tag_data=None,
                      index=0):
        """Find the next matching tag.

        Find the next matching tag using tag type attributes, or content.

        Args:
            tag_type: The type of tag to search for.
            tag_attributes: The tag attributes to search for.
            tag_data: The tag data to search for.
            index: the starting point in the flat list of tags.

        Returns:
            The index in the flat list of the next matching tag, or -1.

        """
        self._logger.info("Find next tag")
        self._logger.debug("type = %s, attributes = %s, data = %s, index = %i",
                           str(tag_type), str(tag_attributes), str(tag_data),
                           index)
        if tag_type:
            for i in range(index, self._number_of_tags):
                data = self._parsed_data[i]
                if data[0].lower() == tag_type.lower():
                    match = True
                    if tag_attributes and len(data) > 1:
                        if data[1] != tag_attributes:
                            match = False
                    if tag_data and len(data) > 2:
                        if data[2] != tag_data:
                            match = False
                    if match:
                        self._logger.debug("Matching tag index: %i", i)
                        return i
        self._logger.warning("Tag not found")
        return -1

    def get_tag(self, index):
        """Get the specified tag.

        Args:
            index: The index of the tag in the flat list.

        Returns:
            A list containing:[tag type, nested list with tag attribute tuples,
            and tag content], or None on error.

        """
        self._logger.info("Get tag")
        self._logger.debug("Index: %i", index)
        if index >= 0 and index < len(self._parsed_data):
            return self._parsed_data[index]
        else:
            self._logger.warning("Index out of range")
            return None

    def escape_text(self, text):
        """Replace special characters with HTML escape codes.

        Args:
            text: The text to escape.

        Returns:
            The escaped text.

        """
        self._logger.info("Escape text")
        self._logger.debug("Text: %s", text)
        if text:
            text = cgi.escape(text, quote=True).encode('ascii',
                                                       'xmlcharrefreplace')
            text = text.replace("'", "&#039;")
        self._logger.debug("Escaped text: %s", text)
        return text

    def unescape_text(self, text):
        """Replace HTML escape codes with special characters.

        Args:
            text: The text to unescape.

        Returns:
            The unescaped text.

        """
        self._logger.info("Unescape text")
        self._logger.debug("Text: %s", text)
        if text:
            text = text.replace("&quot;", "\"")
            text = text.replace("&#039;", "'")
            text = text.replace("&lt;", "<")
            text = text.replace("&gt;", ">")
            text = text.replace("&nbsp;", " ")
            text = text.replace("&amp;", "&")
        self._logger.debug("Unescaped text: %s", text)
        return text

