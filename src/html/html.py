"""This module provides an HTML parsing class.

    Packages(s) required:
    - cgi
    - contextlib
    - datetime
    - HTMLParser
    - requests
    - sys
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
import requests
import sys
import time
import urllib2
#from __future__ import with_statement # required if using Python 2.5


class Error(Exception):
    """General base exception class for this module."""
    pass


class Tag(object):
    """Describes an HTML tag.

    Attributes:
        name: The name/type of a tag. e.g., 'table'.
        attributes: A list of attribute tuples.
        data: The content of the Tag.
        parent: The parent of the Tag.
        children: A list of Tag children objects.
        string_concat_list: A list used for string concatenations.

    """
    # Public member variables
    name = None
    attributes = None
    data = None
    parent = None
    children = None
    string_concat_list = None # List used for string concatenations

    def __init__(self, name=None, attributes=None, data=None, parent=None,
                 children=None):
        """Create and initialize a Tag.

        Args:
            name: The name/type of a tag. e.g., 'table'.
            attributes: A list of attribute tuples.
            data: The content of the Tag.
            parent: The parent of the Tag.
            children: A list of Tag children objects.

        """
        self.name = name
        self.attributes = attributes
        self.data = data
        self.parent = parent
        self.children = children
        self.string_concat_list = []


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
    _debug = False
    _debug_output = sys.stdout  # Output to the screen
    _parsed_data = None
    _root = None
    _current_tag = None
    _number_of_tags = None
    _last_request_time = None  # date/time of last HTTP request
    _rate_limit_counter_time = None  # date/time for rate limit periods
    _rate_limit_count = 0  # number of HTTP requests during this rate period

    def __init__(self):
        """Create and initialize the HTML parser.

        Prepare the parent class for processing, reset the root Tag, tag
        counter, and rate limiting.

        """
        self._parsed_data = []
        self._root = Tag(name='root', children=[])
        self._current_tag = self._root
        self._number_of_tags = 0
        HTMLParser.HTMLParser.__init__(self)
        self._rate_limit_counter_time = datetime.datetime.now()

    def parse_file(self, file_name):
        """Parse an HTML file.

        Args:
            file_name: The HTML file to parse.

        Returns:
            True if theh file was parsed successfully.

        """
        html_file = None
        # If a file is specified, open it
        if file_name and len(file_name) > 0:
            if self._debug:
                self._debug_output.write("HTML: Parsing the file: %s\n" %
                                         (str(file_name)))
                self._debug_output.flush()
            try:
                # Open the file
                with open(file_name) as html_file:
                    # Read the markup text
                    data = html_file.read()
            except IOError as excep:
                if self._debug:
                    self._debug_output.write("HTML: IOError while opening the "
                                             "file %s - %s\n" %
                                             (str(file_name), str(excep)))
                    self._debug_output.flush()
                raise Error("Error opening the file")

            # Parse the markup text
            return self.parse(data)
        else:
            if self._debug:
                self._debug_output.write("HTML: No file specified\n")
                self._debug_output.flush()
        return False

    def parse_url(self, url, wait_for_rate_limiting=True):
        """Download and parse a URL.

        Args:
            url: The URL to parse.
            wait_for_rate_limiting: True to block for rating limiting.

        Returns:
            True if the URL was parsed successfully.

        """
        html_file = None
        # If a url is specified, open it
        if url and len(url) > 0:
            if self._debug:
                self._debug_output.write("HTML: Parsing the url: %s\n" %
                                         (str(url)))
                self._debug_output.flush()

            # Check rate limiting
            if not self.check_rate_limiting(wait_for_rate_limiting):
                return False

            # Store the time when the request is made
            current_time = datetime.datetime.now()

            try:
                # Open the url
                with contextlib.closing(urllib2.urlopen(url)) as html_file:
                    # Read the markup text
                    data = html_file.read()
            except urllib2.URLError as excep:
                if self._debug:
                    self._debug_output.write("HTML: URLError while opening the "
                                             "url %s - %s\n" %
                                             (str(url), str(excep)))
                    self._debug_output.flush()
                raise Error("Error opening the url")

            # Update rate limit info
            self._last_request_time = datetime.datetime.now()
            if ((current_time - self._rate_limit_counter_time) >
                datetime.timedelta(minutes=1)):
                self._rate_limit_counter_time = self._last_request_time
                self._rate_limit_count = 0
            self._rate_limit_count += 1

            # Parse the markup text
            return self.parse(data)
        else:
            if self._debug:
                self._debug_output.write("HTML: No URL specified\n")
                self._debug_output.flush()
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
            if self._debug:
                self._debug_output.write("HTML: Parsing the url with POST form:"
                                         " %s\n" % (str(url)))
                self._debug_output.flush()

            # Check rate limiting
            if not self.check_rate_limiting(wait_for_rate_limiting):
                return False

            # Store the time when the request is made
            current_time = datetime.datetime.now()

            try:
                # Make the POST request to the url
                with contextlib.closing(requests.post(url,
                                                      data=form_data)) as req:
                    data = req.text
            except requests.ConnectionError as excep:
                if self._debug:
                    self._debug_output.write("HTML: ConnectionError while "
                                             "opening the url with form "
                                             "%s - %s\n" %
                                             (str(url), str(excep)))
                    self._debug_output.flush()
                raise Error("Error opening the url")
            except requests.HTTPError as excep:
                if self._debug:
                    self._debug_output.write("HTML: HTTPError while opening the"
                                             " url with form %s - %s\n" %
                                             (str(url), str(excep)))
                    self._debug_output.flush()
                raise Error("Error opening the url")
            except requests.Timeout as excep:
                if self._debug:
                    self._debug_output.write("HTML: Timeout while opening the "
                                             "url with form %s - %s\n" %
                                             (str(url), str(excep)))
                    self._debug_output.flush()
                raise Error("Error opening the url")
            except requests.TooManyRedirects as excep:
                if self._debug:
                    self._debug_output.write("HTML: TooManyRedirects while "
                                             "opening the url with form "
                                             "%s - %s\n" %
                                             (str(url), str(excep)))
                    self._debug_output.flush()
                raise Error("Error opening the url")

            # Update rate limit info
            self._last_request_time = datetime.datetime.now()
            if ((current_time - self._rate_limit_counter_time) >
                datetime.timedelta(minutes=1)):
                self._rate_limit_counter_time = self._last_request_time
                self._rate_limit_count = 0
            self._rate_limit_count += 1

            # Parse the markup text
            return self.parse(data)
        else:
            if self._debug:
                self._debug_output.write("HTML: No URL or form data "
                                         "specified\n")
                self._debug_output.flush()
        return False

    def check_rate_limiting(self, wait_for_rate_limiting=True):
        """Check for rate limiting.

        Check the rate limiting and optionally pause if required to avoid
        exceeding the rate limit.

        Args:
            wait_for_rate_limiting: True to block for rating limiting.

        Returns:
            True if rate limit was handled properly.

        """
        # Check rate limiting: time between requests
        current_time = datetime.datetime.now()
        if (self._last_request_time and
            ((current_time - self._last_request_time) <
            datetime.timedelta(seconds=self.minimum_time_between_requests))):
            if wait_for_rate_limiting:
                time.sleep(self.minimum_time_between_requests)
            else:
                return False

        # Check rate limiting: requests per minute
        current_time = datetime.datetime.now()      # Get current time
        if self._rate_limit_count >= self.requests_per_minute:
            if wait_for_rate_limiting:
                rate_delay = (60 -
                              (current_time -
                              self._rate_limit_counter_time).seconds)
                if rate_delay > 0:
                    time.sleep(rate_delay)
                else:
                    time.sleep(self.minimum_time_between_requests)
            else:
                return False

        # Rate limiting not needed, or it was and we waited the required time
        return True

    def parse(self, markup_text):
        """Parse HTML markup.

        Args:
            markup_text: The HTML markup text to parse.

        Returns:
            True if the markup was parsed successfully.

        """
        # Start with the root of the document
        self._parsed_data = []
        self._root = Tag(name='root', children=[])
        self._current_tag = self._root
        self._number_of_tags = 0
        self.reset()

        # Fix any issues before we call the parser
        if markup_text:
            markup_text = markup_text.replace('</>', '</a>')
            try:
                # Feed our data to the parser
                self.feed(markup_text)
            except HTMLParser.HTMLParseError as excep:
                if self._debug:
                    self._debug_output.write("HTML: HTMLParseError while "
                                             "parsing the HTML - %s\n" %
                                             str(excep))
                    self._debug_output.flush()
                raise Error("Error parsing HTML")
        # Store the root tag to the list of HTML tags
        self.store_tag(self._root)
        self._number_of_tags = len(self._parsed_data)
        if self._debug:
            self._debug_output.write("HTML: finished parsing. Position "
                                     "- %s\n" % str(self.getpos()))
            self._debug_output.write("HTML: %s tags processed\n" %
                                     str(self._number_of_tags))
            #for i in range(0, self._number_of_tags):
            #   self._debug_output.write("%s\n" % str(self._parsed_data[i]))
            self._debug_output.flush()

        return True

    def store_tag(self, tag):
        """Store the current tag.

        Args:
            tag: The Tag object to store in the flat list.

        """
        if tag:
            # Store the tag data to the list of tags
            self._parsed_data.append([tag.name, tag.attributes, tag.data])
            # If the tag has children, recursively call this function to
            # store them as well
            if tag.children and len(tag.children) > 0:
                for i in range(0, len(tag.children)):
                    self.store_tag(tag.children[i])

    def handle_starttag(self, tag, attrs):
        """Handle the start of an HTML tag.

        Event handler for when the start of a tag is encountered.

        Args:
            tag: The HTML tag.
            attrs: A list of the tag's attributes.

        """
        if self._debug:
            self._debug_output.write("HTML: start tag - %s / %s\n" %
                                     (tag, str(attrs)))
            self._debug_output.flush()
        new_tag = Tag(name=tag, attributes=attrs, parent=self._current_tag,
                      data='')
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
        if self._debug:
            self._debug_output.write("HTML: end tag - %s\n" % tag)
            self._debug_output.flush()
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
        if self._debug:
            self._debug_output.write("HTML: start/end tag - %s / %s\n" %
                                     (tag, str(attrs)))
            self._debug_output.flush()
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
        if self._debug:
            self._debug_output.write("HTML: data - %s\n" % data)
            self._debug_output.flush()
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
        if self._debug:
            self._debug_output.write("HTML: comment - %s\n" % data)
            self._debug_output.flush()
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
        if self._debug:
            self._debug_output.write("HTML: declaration - %s\n" % decl)
            self._debug_output.flush()
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
        if self._debug:
            self._debug_output.write("HTML: declaration - %s\n" % data)
            self._debug_output.flush()
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
                        return i
        return -1

    def get_tag(self, index):
        """Get the specified tag.

        Args:
            index: The index of the tag in the flat list.

        Returns:
            A list containing:[tag type, nested list with tag attribute tuples,
            and tag content], or None on error.

        """
        if index >= 0 and index < len(self._parsed_data):
            return self._parsed_data[index]
        else:
            return None

    def escape_text(self, text):
        """Replace special characters with HTML escape codes.

        Args:
            text: The text to escape.

        Returns:
            The escaped text.

        """
        if not text:
            return None
        text = cgi.escape(text, quote=True).encode('ascii',
                                                   'xmlcharrefreplace')
        return text.replace("'", "&#039;")

    def unescape_text(self, text):
        """Replace HTML escape codes with special characters.

        Args:
            text: The text to unescape.

        Returns:
            The unescaped text.

        """
        if text:
            text = text.replace("&quot;", "\"")
            text = text.replace("&#039;", "'")
            text = text.replace("&lt;", "<")
            text = text.replace("&gt;", ">")
            text = text.replace("&nbsp;", " ")
            text = text.replace("&amp;", "&")
        return text
