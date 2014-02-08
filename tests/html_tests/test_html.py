"""This module tests functions in the HTML class.

    Packages(s) required:
    - datetime
    - html
    - time
    - pytest
    - logging
    - sys

"""

# Imports
import datetime
import logging
import pytest
import sys
import time

import sys,os
sys.path.append(os.path.realpath('..'))
from html import html
from html import atom


class TestHtml:
    """Test the HTML class."""

    def setup_method(self, method):
        """Setup each test."""
        formatter = logging.Formatter('%(asctime)s - %(levelname)s:'
                                      '%(name)s:%(message)s')
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self.h = html.HTML(handler)

    def test_escape_text_all_symbols(self):
        text = "& \" ' < >"
        expected_result = "&amp; &quot; &#039; &lt; &gt;"
        assert self.h.escape_text(text) == expected_result

    def test_escape_text_all_escape_codes(self):
        text = "&amp; &quot; &#039; &lt; &gt;"
        expected_result = "&amp; &quot; &#039; &lt; &gt;"
        assert self.h.escape_text(text) == expected_result

    def test_escape_text_none_as_input(self):
        text = None
        expected_result = None
        assert self.h.escape_text(text) == expected_result

    def test_unescape_text_all_escaped_symbols(self):
        text = "&amp; &quot; &#039; &lt; &gt;"
        expected_result = "& \" ' < >"
        assert self.h.unescape_text(text) == expected_result

    def test_unescape_text_all_symbols(self):
        text = "& \" ' < >"
        expected_result = "& \" ' < >"
        assert self.h.unescape_text(text) == expected_result

    def test_unescape_text_none_as_input(self):
        text = None
        expected_result = None
        assert self.h.unescape_text(text) == expected_result

    def test_handle_starttag_empty_tag_named_mytag(self):
        tag = "mytag"
        attrs = []
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data
        assert self.h._current_tag.parent.name == expected_parent_tag
        assert self.h._current_tag in self.h._current_tag.parent.children
        assert self.h._current_tag.children == expected_children

    def test_handle_starttag_mytag_with_attributes(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data
        assert self.h._current_tag.parent.name == expected_parent_tag
        assert self.h._current_tag in self.h._current_tag.parent.children
        assert self.h._current_tag.children == expected_children

    def test_handle_starttag_none_as_tagname(self):
        tag = None
        attrs = []
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data
        assert self.h._current_tag.parent.name == expected_parent_tag
        assert self.h._current_tag in self.h._current_tag.parent.children
        assert self.h._current_tag.children == expected_children

    def test_handle_starttag_none_as_attributes(self):
        tag = "mytag"
        attrs = None
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data
        assert self.h._current_tag.parent.name == expected_parent_tag
        assert self.h._current_tag in self.h._current_tag.parent.children
        assert self.h._current_tag.children == expected_children

    def test_handle_data_simple_tag_with_simple_data(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = 'my data'
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == data

    def test_handle_data_none_as_data(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = None
        expected_data = ''
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data

    def test_handle_data_data_with_only_carriage_return_newline(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = '\r\n'
        expected_data = ''
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data

    def test_handle_data_data_with_cr_nl_inside_text(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = 'my\rdata\ntest'
        expected_data = 'mydatatest'
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data

    def test_handle_data_appending_through_multiple_calls(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data1 = 'mydata'
        data2 = 'test'
        expected_data = 'mydatatest'
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data1)
        self.h.handle_data(data2)
        assert self.h._current_tag.name == tag
        assert self.h._current_tag.attributes == attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_data

    def test_handle_endtag_em_tag(self):
        parent_tag = "mytag"
        parent_attrs = []
        tag = "em"
        attrs = []
        data1 = 'my data'
        data2 = 'test'
        expected_full_data = "my datatest"
        # Preconditions
        self.h.handle_starttag(parent_tag, parent_attrs)
        self.h.handle_data(data1)
        self.h.handle_starttag(tag, attrs)
        self.h.handle_data(data2)
        self.h.handle_endtag(tag)
        # current_tag should now be parent_tag and current_tag data should be appended to parent_tag data
        assert self.h._current_tag.name == parent_tag
        assert self.h._current_tag.attributes == parent_attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_full_data

    def test_handle_endtag_all_other_tags(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = 'my data'
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        # Preconditions
        self.h.handle_starttag(tag, attrs)
        self.h.handle_data(data)
        self.h.handle_endtag(tag)
        # current_tag should now be root again
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert self.h._current_tag.data == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == tag
        assert self.h._current_tag.children[0].attributes == attrs
        assert self.h._current_tag.children[0].data == data

    def test_handle_startendtag_br_tag(self):
        parent_tag = "xyz"
        parent_attrs = []
        tag = "br"
        attrs = [('id', 'lga')]
        expected_parent_data = ' '
        # Preconditions
        self.h.handle_starttag(parent_tag, parent_attrs)
        self.h.handle_startendtag(tag, attrs)
        # current_tag should still be parent tag
        assert self.h._current_tag.name == parent_tag
        assert self.h._current_tag.attributes == parent_attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_parent_data
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == tag
        assert self.h._current_tag.children[0].attributes == attrs
        assert self.h._current_tag.children[0].parent.name == parent_tag

    def test_handle_startendtag_all_other_tags(self):
        parent_tag = "xyz"
        parent_attrs = []
        tag = "mytag"
        attrs = [('id', 'lga')]
        expected_parent_data = ''
        # Preconditions
        self.h.handle_starttag(parent_tag, parent_attrs)
        self.h.handle_startendtag(tag, attrs)
        # current_tag should still be parent tag
        assert self.h._current_tag.name == parent_tag
        assert self.h._current_tag.attributes == parent_attrs
        assert ''.join(self.h._current_tag.string_concat_list) == expected_parent_data
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == tag
        assert self.h._current_tag.children[0].attributes == attrs
        assert self.h._current_tag.children[0].parent.name == parent_tag

    def test_handle_comment_normal_data(self):
        data = "my data"
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root with comment tag appended to children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == expected_tag
        assert self.h._current_tag.children[0].attributes == expected_attributes
        assert self.h._current_tag.children[0].data == data
        assert self.h._current_tag.children[0].parent.name == expected_root_tag

    def test_handle_comment_data_with_only_carriage_return_and_newline(self):
        data = "\r\n"
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root no children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 0

    def test_handle_comment_string_with_cr_nl_inside(self):
        data = "my\rdata\ntest"
        expected_data = "mydatatest"
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root with comment tag appended to children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == expected_tag
        assert self.h._current_tag.children[0].attributes == expected_attributes
        assert self.h._current_tag.children[0].data == expected_data
        assert self.h._current_tag.children[0].parent.name == expected_root_tag

    def test_handle_comment_none_as_data(self):
        data = None
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root with 0 children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 0

    def test_handle_decl_normal_data(self):
        data = "my data"
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root with declaration tag appended to children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == expected_tag
        assert self.h._current_tag.children[0].attributes == expected_attributes
        assert self.h._current_tag.children[0].data == data
        assert self.h._current_tag.children[0].parent.name == expected_root_tag

    def test_handle_decl_data_with_only_carriage_return_and_newline(self):
        data = "\r\n"
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root no children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 0

    def test_handle_decl_string_with_cr_nl_inside(self):
        data = "my\rdata\ntest"
        expected_data = "mydatatest"
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root with declaration tag appended to children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == expected_tag
        assert self.h._current_tag.children[0].attributes == expected_attributes
        assert self.h._current_tag.children[0].data == expected_data
        assert self.h._current_tag.children[0].parent.name == expected_root_tag

    def test_handle_decl_none_as_data(self):
        data = None
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root with 0 children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 0

    def test_unknown_decl_normal_data(self):
        data = "my data"
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root with unknown_declaration tag appended to children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == expected_tag
        assert self.h._current_tag.children[0].attributes == expected_attributes
        assert self.h._current_tag.children[0].data == data
        assert self.h._current_tag.children[0].parent.name == expected_root_tag

    def test_unknown_decl_data_with_only_carriage_return_and_newline(self):
        data = "\r\n"
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root no children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 0

    def test_unknown_decl_string_with_cr_nl_inside(self):
        data = "my\rdata\ntest"
        expected_data = "mydatatest"
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root with unknown_declaration tag appended to children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 1
        assert self.h._current_tag.children[0].name == expected_tag
        assert self.h._current_tag.children[0].attributes == expected_attributes
        assert self.h._current_tag.children[0].data == expected_data
        assert self.h._current_tag.children[0].parent.name == expected_root_tag

    def test_unknown_decl_none_as_data(self):
        data = None
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = ''
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root with 0 children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._current_tag.attributes == expected_root_attributes
        assert ''.join(self.h._current_tag.string_concat_list) == expected_root_data
        assert self.h._current_tag.parent == expected_root_parent
        assert len(self.h._current_tag.children) == 0

    def test_store_tag_tag_with_data_but_no_children(self):
        tag_name = "mytag"
        attrs = [('id', 'lga')]
        tag_children = None
        tag_data = "my data"
        tag = atom.Tag(name=tag_name, attributes=attrs, children=tag_children, data=tag_data)
        self.h._store_tag(tag)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert len(self.h._parsed_data) == 1
        assert self.h._parsed_data[0][0] == tag_name
        assert self.h._parsed_data[0][1] == attrs
        assert self.h._parsed_data[0][2] == tag_data

    def test_store_tag_tag_as_none(self):
        tag = None
        self.h._store_tag(tag)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert len(self.h._parsed_data) == 0

    def test_store_tag_tag_with_data_and_children(self):
        tag_name1 = "mytag1"
        attrs1 = [('id', 'lga')]
        tag_children1 = None
        tag_data1 = "my data1"
        tag1 = atom.Tag(name=tag_name1, attributes=attrs1, children=tag_children1, data=tag_data1)
        tag_name2 = "mytag2"
        attrs2 = [('id', 'lga')]
        tag_children2 = None
        tag_data2 = "my data2"
        tag2 = atom.Tag(name=tag_name2, attributes=attrs2, children=tag_children2, data=tag_data2)
        tag_name3 = "mytag3"
        attrs3 = [('id', 'lga')]
        tag_children3 = [tag1, tag2]
        tag_data3 = "my data3"
        tag3 = atom.Tag(name=tag_name3, attributes=attrs3, children=tag_children3, data=tag_data3)
        self.h._store_tag(tag3)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert len(self.h._parsed_data) == 3
        assert self.h._parsed_data[0][0] == tag_name3
        assert self.h._parsed_data[0][1] == attrs3
        assert self.h._parsed_data[0][2] == tag_data3
        assert self.h._parsed_data[1][0] == tag_name1
        assert self.h._parsed_data[1][1] == attrs1
        assert self.h._parsed_data[1][2] == tag_data1
        assert self.h._parsed_data[2][0] == tag_name2
        assert self.h._parsed_data[2][1] == attrs2
        assert self.h._parsed_data[2][2] == tag_data2

    def test_check_rate_limiting_not_limited(self):
        wait = False
        expected_result = True
        current_time = datetime.datetime.now()
        self.h.minimum_time_between_requests = 30
        self.h.requests_per_minute = 5
        self.h._last_request_time = current_time - datetime.timedelta(seconds=35)
        self.h._rate_limit_count = 3
        self.h._rate_limit_counter_time = current_time - datetime.timedelta(seconds=5)
        start_time = time.time()
        assert self.h._check_rate_limiting(wait) == expected_result
        elapsed_time = time.time() - start_time
        assert elapsed_time < 1

    def test_check_rate_limiting_limited_between_requests_wait(self):
        wait = True
        expected_result = True
        current_time = datetime.datetime.now()
        self.h.minimum_time_between_requests = 30
        self.h.requests_per_minute = 5
        self.h._last_request_time = current_time - datetime.timedelta(seconds=20)
        self.h._rate_limit_count = 3
        self.h._rate_limit_counter_time = current_time - datetime.timedelta(seconds=5)
        start_time = time.time()
        assert self.h._check_rate_limiting(wait) == expected_result
        elapsed_time = time.time() - start_time
        assert elapsed_time > 30
        assert elapsed_time < 31

    def test_check_rate_limiting_limited_between_requests_no_wait(self):
        wait = False
        expected_result = False
        current_time = datetime.datetime.now()
        self.h.minimum_time_between_requests = 30
        self.h.requests_per_minute = 5
        self.h._last_request_time = current_time - datetime.timedelta(seconds=20)
        self.h._rate_limit_count = 3
        self.h._rate_limit_counter_time = current_time - datetime.timedelta(seconds=5)
        start_time = time.time()
        assert self.h._check_rate_limiting(wait) == expected_result
        elapsed_time = time.time() - start_time
        assert elapsed_time > 0
        assert elapsed_time < 1

    def test_check_rate_limiting_limited_per_minute_wait_remaining_time(self):
        wait = True
        expected_result = True
        current_time = datetime.datetime.now()
        self.h.minimum_time_between_requests = 30
        self.h.requests_per_minute = 5
        self.h._last_request_time = current_time - datetime.timedelta(seconds=35)
        self.h._rate_limit_count = 5
        self.h._rate_limit_counter_time = current_time - datetime.timedelta(seconds=5)
        start_time = time.time()
        assert self.h._check_rate_limiting(wait) == expected_result
        elapsed_time = time.time() - start_time
        assert elapsed_time > 54
        assert elapsed_time < 56

    def test_check_rate_limiting_limited_per_minute_wait_between_time(self):
        wait = True
        expected_result = True
        current_time = datetime.datetime.now()
        self.h.minimum_time_between_requests = 30
        self.h.requests_per_minute = 5
        self.h._last_request_time = current_time - datetime.timedelta(seconds=35)
        self.h._rate_limit_count = 5
        self.h._rate_limit_counter_time = current_time - datetime.timedelta(seconds=61)
        start_time = time.time()
        assert self.h._check_rate_limiting(wait) == expected_result
        elapsed_time = time.time() - start_time
        assert elapsed_time > 30
        assert elapsed_time < 31

    def test_check_rate_limiting_limited_per_minute_no_wait(self):
        wait = False
        expected_result = False
        current_time = datetime.datetime.now()
        self.h.minimum_time_between_requests = 30
        self.h.requests_per_minute = 5
        self.h._last_request_time = current_time - datetime.timedelta(seconds=35)
        self.h._rate_limit_count = 5
        self.h._rate_limit_counter_time = current_time - datetime.timedelta(seconds=5)
        start_time = time.time()
        assert self.h._check_rate_limiting(wait) == expected_result
        elapsed_time = time.time() - start_time
        assert elapsed_time > 0
        assert elapsed_time < 1

    def test_parse_markup_as_none(self):
        text = None
        expected_result = True
        expected_root_tag = 'root'
        expected_root_children = []
        expected_tag_count = 1
        assert self.h.parse(text) == expected_result
        assert len(self.h._parsed_data) == expected_tag_count
        assert self.h._parsed_data[0][0] == expected_root_tag
        assert self.h._root.name == expected_root_tag
        assert self.h._root.children == expected_root_children
        assert self.h._current_tag.name == expected_root_tag
        assert self.h._number_of_tags == expected_tag_count

    def test_parse_good_html_with_several_tags(self):
        text = "<b>my data</b><i>test</i><br/>"
        expected_result = True
        expected_root_tag = 'root'
        expected_root_children = 3
        expected_tag_count = 4
        expected_tag_name1 = "b"
        expected_tag_data1 = "my data"
        expected_tag_name2 = "i"
        expected_tag_data2 = "test"
        expected_tag_name3 = "br"
        assert self.h.parse(text) == expected_result
        assert self.h._root.name == expected_root_tag
        assert len(self.h._root.children) == expected_root_children
        assert self.h._number_of_tags == expected_tag_count
        assert len(self.h._parsed_data) == expected_tag_count
        assert self.h._parsed_data[0][0] == expected_root_tag
        assert self.h._parsed_data[1][0] == expected_tag_name1
        assert self.h._parsed_data[1][2] == expected_tag_data1
        assert self.h._parsed_data[2][0] == expected_tag_name2
        assert self.h._parsed_data[2][2] == expected_tag_data2
        assert self.h._parsed_data[3][0] == expected_tag_name3

    def test_parse_html_with_endtag_as_only_slash(self):
        text = "<a href=\"test\">test</><br/>"
        expected_result = True
        expected_root_tag = 'root'
        expected_root_children = 2
        expected_tag_count = 3
        expected_tag_name1 = "a"
        expected_tag_data1 = "test"
        expected_tag_name2 = "br"
        assert self.h.parse(text) == expected_result
        assert self.h._root.name == expected_root_tag
        assert len(self.h._root.children) == expected_root_children
        assert self.h._number_of_tags == expected_tag_count
        assert len(self.h._parsed_data) == expected_tag_count
        assert self.h._parsed_data[0][0] == expected_root_tag
        assert self.h._parsed_data[1][0] == expected_tag_name1
        assert self.h._parsed_data[1][2] == expected_tag_data1
        assert self.h._parsed_data[2][0] == expected_tag_name2

    def test_parse_file_html_file_as_input(self):
        filename = "tests/files/test.html"
        expected_result = True
        assert self.h.parse_file(filename) == expected_result

    def test_parse_file_non_existant_file(self):
        filename = "tests/files/invalid_file.html"
        with pytest.raises(html.Error):
            self.h.parse_file(filename)

    def test_parse_file_none_as_filename(self):
        filename = None
        expected_result = False
        assert self.h.parse_file(filename) == expected_result

    def test_parse_url_google_as_input(self):
        url = "http://www.google.com"
        expected_result = True
        assert self.h.parse_url(url) == expected_result

    def test_parse_url_non_existant_url(self):
        url = "http://asdf1974jgladslf.com"
        with pytest.raises(html.Error):
            self.h.parse_url(url)

    def test_parse_url_none_as_url(self):
        url = None
        expected_result = False
        assert self.h.parse_url(url) == expected_result

    def test_parse_url_with_post_form_for_ncaa_game_data(self):
        formdata = {
            "sport_code" : "MBB",
            "division" : "1",
            "conf_id" : "-1",
            "academic_year" : "2013",
            "schedule_date" : "2013-11-09",
        }
        url = "http://stats.ncaa.org/team/schedule_list"
        expected_result = True
        assert self.h.parse_url_with_post_form(url, formdata) == expected_result

    def test_parse_url_with_post_form_non_existant_url(self):
        url = "http://asdf1974jgladslf.com"
        formdata = {}
        expected_result = False
        assert self.h.parse_url_with_post_form(url, formdata) == expected_result

    def test_parse_url_with_post_form_none_as_url(self):
        url = None
        formdata = {}
        expected_result = False
        assert self.h.parse_url_with_post_form(url, formdata) == expected_result

    def test_parse_url_with_post_form_none_as_post_data(self):
        url = "http://www.google.com"
        formdata = None
        expected_result = False
        assert self.h.parse_url_with_post_form(url, formdata) == expected_result

    def test_find_first_tag_all_inputs_none(self):
        type = None
        attr = None
        data = None
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_tag_type_not_found(self):
        type = "aaaaaaaaa"
        attr = None
        data = None
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match(self):
        type = "d"
        attr = None
        data = None
        expected_result = 2
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_one_attribute_missing(self):
        type = "abc"
        attr = [('id', 'lga')]
        data = None
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_one_attribute_not_equal(self):
        type = "abc"
        attr = [('id', 'lga'), ('xy', 'a')]
        data = None
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_attribute_match(self):
        type = "abc"
        attr = [('id', 'lga'), ('xy', 'z')]
        data = None
        expected_result = 1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_data_mismatch(self):
        type = "abc"
        attr = None
        data = "asdf"
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_data_match(self):
        type = "abc"
        attr = None
        data = "data1"
        expected_result = 1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_attributes_match_data_mismatch(self):
        type = "xyz"
        attr = [('id', 'lga'), ('xy', 'z')]
        data = "dddddddd"
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_type_match_attributes_mismatch_data_match(self):
        type = "xyz"
        attr = [('id', 'hhh'), ('xy', 'z')]
        data = "data2"
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_first_tag_everything_matches(self):
        type = "d"
        attr = [('id', '2'), ('xy', 'w')]
        data = "data4"
        expected_result = 3
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_first_tag(type, attr, data) == expected_result

    def test_find_next_tag_type_match(self):
        type = "d"
        attr = None
        data = None
        index = 3
        expected_result = 3
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_next_tag(type, attr, data, index) == expected_result

    def test_find_next_tag_type_and_attribute_match(self):
        type = "d"
        attr = [('id', '1'), ('xy', 'z')]
        data = None
        index = 3
        expected_result = 3
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_next_tag(type, attr, data, index) == expected_result

    def test_find_next_tag_no_more_matching_tags(self):
        type = "abc"
        attr = None
        data = None
        index = 2
        expected_result = -1
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.find_next_tag(type, attr, data, index) == expected_result

    def test_get_tag_negative_index(self):
        index = -1
        expected_result = None
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.get_tag(index) == expected_result

    def test_get_tag_index_greater_than_tag_count(self):
        index = 500
        expected_result = None
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.get_tag(index) == expected_result

    def test_get_tag_index_equal_to_tag_count(self):
        index = 4
        expected_result = None
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = atom.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        assert self.h.get_tag(index) == expected_result

    def test_get_tag_valid_index(self):
        index = 0
        expected_name = "xyz"
        expected_attributes = [('id', 'lga'), ('xy', 'z')]
        expected_data = "data2"
        # Preconditions
        tag1 = atom.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = atom.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = atom.Tag(name=expected_name, attributes=expected_attributes, children=[tag1, tag3, tag4], data=expected_data)
        self.h._store_tag(tag2)
        self.h._number_of_tags = len(self.h._parsed_data)
        newtag = self.h.get_tag(index)
        assert newtag[0] == expected_name
        assert newtag[1] == expected_attributes
        assert newtag[2] == expected_data

