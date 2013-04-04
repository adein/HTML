## @package HTML
#  This module includes functions for processing HTML files.
#
#  @author Aaron DeGrow
#
#  @date Mar 27th, 2012
#
#  @version 0.4
#
#  Packages(s) required:
#  - sys
#  - HTMLParser
#  - urllib
#  - datetime
#  - time
#  - requests
#
#  Version History:
#  - 0.1 First implementation
#  - 0.2 Changed a few code conventions
#  - 0.3 Added rate limiting
#  - 0.4 Added support for POST web forms
#
#  To-do:
#  - Implement/fix case-insensitivity on FindFirst/NextTag
#  - Add GetTag(text, tag_name, starting_index)
#  - Add GetNearestMatch()
#  - Add StripTags()


# Python imports
import sys
import HTMLParser
import urllib
import datetime
import time
import requests


## Class that describes an HTML tag.  Essentially a C-style struct.
class Tag():
    ## The name/type of a tag.  e.g., 'table'
    name_ = None
    ## A list of attribute tuples.  e.g., [('bgcolor', '#FFFFFF')]
    attributes_ = None
    ## The content of the tag.
    data_ = None
    ## The parent Tag for this tag
    parent_ = None
    ## A list of Tag children objects
    children_ = None

    ## Constructor
    #
    #  Create a Tag object with the user-specified properties.
    #
    #  @param name the name/type of the tag (default None).
    #  @param attributes the list of attribute tuples of the tag (default None).
    #  @param data the content of the tag (default None).
    #  @param parent the parent Tag object of this tag (default None).
    #  @param children the list of children Tag objects (default None).
    def __init__(self, name=None, attributes=None, data=None, parent=None, children=None):
        self.name_ = name
        self.attributes_ = attributes
        self.data_ = data
        self.parent_ = parent
        self.children_ = children

## Provide HTML processing in Python
class HTML(HTMLParser.HTMLParser):

    ## Set to "True" for debug output
    debug_ = False

    ## Debug output object
    debug_output_ = sys.stdout              # Output to the screen
    #debug_output_ = open('out.log', 'w')   # Output to a log file

    ## Number of requests allowed per minute for rate limiting
    requests_per_minute_ = 120

    ## Minimum time delay between requests in seconds
    minimum_time_between_requests_ = 0

    ## The flat list of Tag objects that were parsed from the document/URL.
    parsed_data_ = None
    
    ## The top-most/root Tag object for a document/URL that all tags are a children of.
    root_ = None
    
    ## The current Tag object that's being parsed.
    current_tag_ = None
    
    ## The number of Tag objects in the document/URL.
    number_of_tags_ = None
    
    ## Rate limiting variables
    last_request_time_ = None                    # date/time of last HTTP request
    rate_limit_counter_time_ = None              # date/time for rate limit periods
    rate_limit_count_ = 0                        # number of HTTP requests during this rate limit period

    ## Constructor
    #
    #  Create an instance of the HTML class, prepare the HTMLParser parent class for processing, 
    #  and reset the root Tag, tag counter, and rate limiting.
    def __init__(self):
        self.parsed_data_ = []
        self.root_ = Tag(name='root', children=[])
        self.current_tag_ = self.root_
        self.number_of_tags_ = 0
        HTMLParser.HTMLParser.__init__(self)
        self.rate_limit_counter_time_ = datetime.datetime.now()

    ## Parse an HTML file
    #
    #  @param file_name HTML file to parse (default None).
    #  @return True if the file was parsed succesfully.
    def ParseFile(self, file_name=None):
        file = None
        try:
            # If a file is specified, open it
            if (file_name is not None and len(file_name) > 0):
                if (self.debug_):
                    self.debug_output_.write("HTML: Parsing the file: %s\n" % (str(file_name)))
                    self.debug_output_.flush()
                    
                # Open the file
                file = open(file_name)
                
                # Read the markup text
                data = file.read()
                
                # Parse the markup text
                return self.Parse(data)
            else:
                if (self.debug_):
                    self.debug_output_.write("HTML: No file specified" + "\n")
                    self.debug_output_.flush()
        except Exception, e:
            if (self.debug_):
                self.debug_output_.write("HTML: Error reading the file " + str(e) + "\n")
                self.debug_output_.flush()
        finally:
            if (file is not None):
                file.close()
        return False

    ## Download and parse a URL
    #
    #  @param url URL to parse (default None).
    #  @param wait_for_rate_limiting True if the function should block for rate limiting (default True).
    #  @return True if the URL was parsed succesfully.
    def ParseURL(self, url=None, wait_for_rate_limiting=True):
        file = None
        try:
            # If a url is specified, open it
            if (url is not None and len(url) > 0):
                if (self.debug_):
                    self.debug_output_.write("HTML: Parsing the url: %s\n" % (str(url)))
                    self.debug_output_.flush()

                # Check rate limiting
                if (not self.CheckRateLimiting(wait_for_rate_limiting)):
                    return False

                # Store the time when the request is made
                current_time = datetime.datetime.now()
                
                # Open the url
                file = urllib.urlopen(url)
                
                # Read the markup text
                data = file.read()
                
                # Update rate limit info
                self.last_request_time_ = datetime.datetime.now()
                if ((current_time - self.rate_limit_counter_time_) > datetime.timedelta(minutes=1)):
                    self.rate_limit_counter_time_ = self.last_request_time_
                    self.rate_limit_count_ = 0
                self.rate_limit_count_ += 1
                
                # Parse the markup text
                return self.Parse(data)
            else:
                if (self.debug_):
                    self.debug_output_.write("HTML: No URL specified" + "\n")
                    self.debug_output_.flush()
        except Exception, e:
            if (self.debug_):
                self.debug_output_.write("HTML: Error reading the URL " + str(e) + "\n")
                self.debug_output_.flush()
        finally:
            if (file is not None):
                file.close()
        return False

    ## Download and parse a URL using a POST form
    #
    #  @param url URL to parse (default None).
    #  @param form_data a dictionary containing name/value pairs of the web form data (default None).
    #  @param wait_for_rate_limiting True if the function should block for rate limiting (default True).
    #  @return True if the URL was parsed succesfully.
    def ParseURLWithPostForm(self, url=None, form_data=None, wait_for_rate_limiting=True):
        try:
            # If a url is specified, open it
            if (url is not None and len(url) > 0 and form_data is not None):
                if (self.debug_):
                    self.debug_output_.write("HTML: Parsing the url with POST form: %s\n" % (str(url)))
                    self.debug_output_.flush()

                # Check rate limiting
                if (not self.CheckRateLimiting(wait_for_rate_limiting)):
                    return False

                # Store the time when the request is made
                current_time = datetime.datetime.now()

                # Make the POST request to the url
                r = requests.post(url, data=form_data)
                data = r.text

                # Update rate limit info
                self.last_request_time_ = datetime.datetime.now()
                if ((current_time - self.rate_limit_counter_time_) > datetime.timedelta(minutes=1)):
                    self.rate_limit_counter_time_ = self.last_request_time_
                    self.rate_limit_count_ = 0
                self.rate_limit_count_ += 1
                
                # Parse the markup text
                return self.Parse(data)
            else:
                if (self.debug_):
                    self.debug_output_.write("HTML: No URL or form data specified" + "\n")
                    self.debug_output_.flush()
        except Exception, e:
            if (self.debug_):
                self.debug_output_.write("HTML: Error reading the URL " + str(e) + "\n")
                self.debug_output_.flush()
        return False

    ## Check for rate limiting.
    #
    #  Check the rate limiting and optionally pause if required to avoid exceeding the rate limit.
    #
    #  @param wait_for_rate_limiting True if the function should block for rate limiting (default True).
    #  @return True if the rate limit was handled properly, False if the rate is exceeded and we didn't wait.
    def CheckRateLimiting(wait_for_rate_limiting=True):
        # Check rate limiting: time between requests
        current_time = datetime.datetime.now()
        if (self.last_request_time_ is not None and ((current_time - self.last_request_time_) < datetime.timedelta(seconds=self.minimum_time_between_requests_))):
            if (wait_for_rate_limiting):
                time.sleep(self.minimum_time_between_requests_)
            else:
                return False

        # Check rate limiting: requests per minute
        current_time = datetime.datetime.now()      # Get current time
        if (self.rate_limit_count_ >= self.requests_per_minute_):
            if (wait_for_rate_limiting):
                rate_delay = 60 - (current_time - self.rate_limit_counter_time_).seconds
                if (rate_delay > 0):
                    time.sleep(rate_delay)
                else:
                    time.sleep(self.minimum_time_between_requests_)
            else:
                return False
                
        # Rate limiting not needed, or it was and we waited the required time
        return True

    ## Parse HTML markup text.
    #
    #  @param markup_text The HTML markup text to parse (default None).
    #  @return True if the markup was parsed succesfully.
    def Parse(self, markup_text=None):
        try:
            # Start with the root of the document
            self.parsed_data_ = []
            self.root_ = Tag(name='root', children=[])
            self.current_tag_ = self.root_
            self.number_of_tags_ = 0
            self.reset()
            
            # Fix any issues before we call the parser
            if (markup_text is not None):
                markup_text = markup_text.replace('</>','</a>')
                # Feed our data to the parser
                self.feed(markup_text)
                
            # Close the document/http connection
            self.close()
            
            # Store the root tag to the list of HTML tags
            self.StoreTag(self.root_)
            self.number_of_tags_ = len(self.parsed_data_)
            if (self.debug_):
                self.debug_output_.write("HTML: finished parsing. Position - " + str(self.getpos()) + "\n")
                self.debug_output_.write("HTML: " + str(self.number_of_tags_) + " tags processed\n")
                #for i in range(0, self.number_of_tags_):
                #       self.debug_output_.write(str(self.parsed_data_[i]) + "\n")
                self.debug_output_.flush()
                
            return True
        except HTMLParser.HTMLParseError, e:
            if (self.debug_):
                self.debug_output_.write("HTML: HTMLParseError while parsing the HTML - " + str(e) + "\n")
                self.debug_output_.flush()
            return False
        except Exception, e:
            if (self.debug_):
                self.debug_output_.write("HTML: Error parsing the HTML markup " + str(e) + "\n")
                self.debug_output_.flush()
            return False

    ## Store the current tag in the flat list parsed_data_
    #
    # @param tag the Tag object to store in the flat list, including it's children Tags.
    def StoreTag(self, tag):
        if (tag is not None):
            # Store the tag data to the list of tags
            self.parsed_data_.append([tag.name_, tag.attributes_, tag.data_])
            # If the tag has children, recursively call this function to store them as well
            if (tag.children_ is not None and len(tag.children_) > 0):
                for i in range(0, len(tag.children_)):
                    self.StoreTag(tag.children_[i])

    ## Handle the start of an HTML tag
    #
    #  Event handler for when the start of a tag is encountered.
    #
    #  @param tag The HTML tag.
    #  @param attrs A list of the tag's attributes.
    def handle_starttag(self, tag, attrs):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: start tag - " + tag + " / " + str(attrs) + "\n")
        #       self.debug_output_.flush()
        new_tag = Tag(name=tag, attributes=attrs, parent=self.current_tag_, data='')
        if (self.current_tag_.children_ is None):
            self.current_tag_.children_ = []
        self.current_tag_.children_.append(new_tag)
        self.current_tag_ = new_tag

    ## Handle the end of an HTML tag
    #
    #  Event handler for when the end of a tag is encountered.
    #
    #  @param tag The HTML tag.
    def handle_endtag(self, tag):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: end tag - " + tag + "\n")
        #       self.debug_output_.flush()
        if (tag == 'em'):
            self.current_tag_.parent_.data_ += self.current_tag_.data_
        self.current_tag_ = self.current_tag_.parent_

    ## Handle a start/end HTML tag
    #
    #  Event handler for when a tag that is both the start and end of a tag is encountered.
    #
    #  @param tag The HTML tag.
    #  @param attrs A list of the tag's attributes.
    def handle_startendtag(self, tag, attrs):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: start/end tag - " + tag + " / " + str(attrs) + "\n")
        #       self.debug_output_.flush()
        if (tag == 'br'):
            if (self.current_tag_.data_ is None):
                self.current_tag_.data_ = ""
            self.current_tag_.data_ += " "
        new_tag = Tag(name=tag, attributes=attrs, parent=self.current_tag_)
        if (self.current_tag_.children_ is None):
            self.current_tag_.children_ = []
        self.current_tag_.children_.append(new_tag)

    ## Handle the data of an HTML tag
    #
    #  Event handler for when the content of a tag is encountered.
    #
    #  @param data The tag's data.
    def handle_data(self, data):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: data - " + data + "\n")
        #       self.debug_output_.flush()
        if (data is not None):
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            if (len(data) > 0):
                if (self.current_tag_.data_ is None):
                    self.current_tag_.data_ = ""
                self.current_tag_.data_ += data

    ## Handle a comment
    #
    #  Event handler for when a comment is encountered.
    #
    #  @param data The comment.
    def handle_comment(self, data):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: comment - " + data + "\n")
        #       self.debug_output_.flush()
        if (data is not None):
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            if (len(data) > 0):
                new_tag = Tag(name='comment', parent=self.current_tag_, data=data)
                if (self.current_tag_.children_ is None):
                    self.current_tag_.children_ = []
                self.current_tag_.children_.append(new_tag)

    ## Handle a declaration
    #
    #  Event handler for when a declaration is encountered.
    #
    #  @param decl The declaration.
    def handle_decl(self, decl):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: declaration - " + decl + "\n")
        #       self.debug_output_.flush()
        if (decl is not None):
            decl = decl.replace("\n", "")
            decl = decl.replace("\r", "")
            if (len(decl) > 0):
                new_tag = Tag(name='declaration', parent=self.current_tag_, data=decl)
                if (self.current_tag_.children_ is None):
                    self.current_tag_.children_ = []
                self.current_tag_.children_.append(new_tag)

    ## Handle an unknown declaration
    #
    #  Event handler for when an unknown declaration is encountered.
    #
    #  @param data The declaration.
    def unknown_decl(self, data):
        #if (self.debug_):
        #       self.debug_output_.write("HTML: declaration - " + data + "\n")
        #       self.debug_output_.flush()
        if (data is not None):
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            if (len(data) > 0):
                new_tag = Tag(name='unknown_declaration', parent=self.current_tag_, data=data)
                if (self.current_tag_.children_ is None):
                    self.current_tag_.children_ = []
                self.current_tag_.children_.append(new_tag)

    ## Find the first matching tag by type, attributes, and content
    #
    #  @param tag_type the type of tag to search for. e.g. 'a' or 'div'.
    #  @param tag_attributes the tag attributes to search for. e.g. [('name', 'somename'), ('type', 'text/css')] (default None).
    #  @param tag_data the tag content to search for. e.g. "Title" (default None).
    #  @return the index in the flat list of the first matching tag, -1 if no match found.
    def FindFirstTag(self, tag_type, tag_attributes=None, tag_data=None):
        return self.FindNextTag(tag_type, tag_attributes, tag_data)

    ## Find next matching tag
    #
    #  @param tag_type the type of tag to search for. e.g. 'A' or 'DIV'.
    #  @param tag_attributes the tag attributes to search for. e.g. [('name', 'somename'), ('type', 'text/css')] (default None).
    #  @param tag_data the tag content to search for. e.g. "Title" (default None).
    #  @param index the starting point in the flat list of tags to start looking (default 0).
    #  @return the index in the list of the matching tag, -1 if no match found.
    def FindNextTag(self, tag_type, tag_attributes=None, tag_data=None, index=0):
        if (tag_type is not None):
            for i in range(index, self.number_of_tags_):
                data = self.parsed_data_[i]
                if (data[0].lower() == tag_type.lower()):
                    match = True
                    if (tag_attributes is not None and len(data) > 1):
                        #data_attr_lower = [(i.lower(),j.lower()) for i,j in data[1]]
                        #tag_attr_lower  = [(i.lower(),j.lower()) for i,j in tag_attributes]
                        #if (data_attr_lower != tag_attr_lower):
                        if (data[1] != tag_attributes):
                            match = False
                    if (tag_data is not None and len(data) > 2):
                        if (data[2] != tag_data):
                            match = False
                    if (match):
                        return i
        return -1

    ## Get the specified tag
    #
    #  @param index the index of the tag to get.
    #  @return A list containing: [the tag type, nested list with tag attribute tuples, and the tag content], or None on error.
    def GetTag(self, index):
        if (index >= 0 and index < len(self.parsed_data_)):
            return self.parsed_data_[index]
        else:
            return None

    ## Replace special characters with HTML escape codes
    #
    #  @param text the text to replace symbols with escape codes (default None).
    #  @return the text with the symbols replaced with escape codes.
    def EscapeText(self, text=None):
        if (text is not None):
            text = text.replace("&", "&amp;")
            text = text.replace("\"", "&quot;")
            text = text.replace("'", "&#039;")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
        return text;

    ## Replace HTML escape codes with special characters
    #
    #  @param text the text to replace escape codes with symbols (default None).
    #  @return the text with the escape codes replaced with symbols.
    def UnescapeText(self, text=None):
        if (text is not None):
            text = text.replace("&amp;", "&")
            text = text.replace("&quot;", "\"")
            text = text.replace("&#039;", "'")
            text = text.replace("&lt;", "<")
            text = text.replace("&gt;", ">")
            text = text.replace("&nbsp;", " ")
        return text;

