## test_HTML
#  This module test functions in the HTML class.
#
#  @author Aaron DeGrow
#
#  @date Mar 27th, 2012
#
#  @version 0.1
#
#  Packages(s) required:
#  - HTML
#
#  Other requirements:
#  - pytest
#
#  Version History:
#  - 0.1 First implementation


# Python imports
import HTML

## Test the HTML class
class TestHTML:

    ## Setup required by each test
    def setup_method(self, method):
        self.h = HTML.HTML()
        self.h.debug_ = True

    def test_EscapeText_all_symbols(self):
        text = "& \" ' < >"
        expected_result = "&amp; &quot; &#039; &lt; &gt;"
        assert self.h.EscapeText(text) == expected_result

    def test_EscapeText_all_escape_codes(self):
        text = "&amp; &quot; &#039; &lt; &gt;"
        expected_result = "&amp; &quot; &#039; &lt; &gt;"
        assert self.h.EscapeText(text) == expected_result

    def test_EscapeText_none_as_input(self):
        text = None
        expected_result = None
        assert self.h.EscapeText(text) == expected_result

    def test_UnescapeText_all_escaped_symbols(self):
        text = "&amp; &quot; &#039; &lt; &gt;"
        expected_result = "& \" ' < >"
        assert self.h.UnescapeText(text) == expected_result

    def test_UnescapeText_all_symbols(self):
        text = "& \" ' < >"
        expected_result = "& \" ' < >"
        assert self.h.UnescapeText(text) == expected_result

    def test_UnescapeText_none_as_input(self):
        text = None
        expected_result = None
        assert self.h.UnescapeText(text) == expected_result

    def test_handle_starttag_empty_tag_named_mytag(self):
        tag = "mytag"
        attrs = []
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data
        assert self.h.current_tag_.parent_.name_ == expected_parent_tag
        assert self.h.current_tag_ in self.h.current_tag_.parent_.children_
        assert self.h.current_tag_.children_ == expected_children

    def test_handle_starttag_mytag_with_attributes(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data
        assert self.h.current_tag_.parent_.name_ == expected_parent_tag
        assert self.h.current_tag_ in self.h.current_tag_.parent_.children_
        assert self.h.current_tag_.children_ == expected_children

    def test_handle_starttag_none_as_tagname(self):
        tag = None
        attrs = []
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data
        assert self.h.current_tag_.parent_.name_ == expected_parent_tag
        assert self.h.current_tag_ in self.h.current_tag_.parent_.children_
        assert self.h.current_tag_.children_ == expected_children

    def test_handle_starttag_none_as_attributes(self):
        tag = "mytag"
        attrs = None
        expected_data = ''
        expected_parent_tag = 'root'
        expected_children = None
        self.h.handle_starttag(tag, attrs)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data
        assert self.h.current_tag_.parent_.name_ == expected_parent_tag
        assert self.h.current_tag_ in self.h.current_tag_.parent_.children_
        assert self.h.current_tag_.children_ == expected_children

    def test_handle_data_simple_tag_with_simple_data(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = 'my data'
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == data

    def test_handle_data_none_as_data(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = None
        expected_data = ''
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data

    def test_handle_data_data_with_only_carriage_return_line_newline(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = '\r\n'
        expected_data = ''
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data

    def test_handle_data_data_with_cr_nl_inside_text(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data = 'my\rdata\ntest'
        expected_data = 'mydatatest'
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data

    def test_handle_data_appending_through_multiple_calls(self):
        tag = "mytag"
        attrs = [('id', 'lga')]
        data1 = 'mydata'
        data2 = 'test'
        expected_data = 'mydatatest'
        self.h.handle_starttag(tag, attrs)  # Precondition
        self.h.handle_data(data1)
        self.h.handle_data(data2)
        assert self.h.current_tag_.name_ == tag
        assert self.h.current_tag_.attributes_ == attrs
        assert self.h.current_tag_.data_ == expected_data

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
        assert self.h.current_tag_.name_ == parent_tag
        assert self.h.current_tag_.attributes_ == parent_attrs
        assert self.h.current_tag_.data_ == expected_full_data

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
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == tag
        assert self.h.current_tag_.children_[0].attributes_ == attrs
        assert self.h.current_tag_.children_[0].data_ == data

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
        assert self.h.current_tag_.name_ == parent_tag
        assert self.h.current_tag_.attributes_ == parent_attrs
        assert self.h.current_tag_.data_ == expected_parent_data
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == tag
        assert self.h.current_tag_.children_[0].attributes_ == attrs
        assert self.h.current_tag_.children_[0].parent_.name_ == parent_tag

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
        assert self.h.current_tag_.name_ == parent_tag
        assert self.h.current_tag_.attributes_ == parent_attrs
        assert self.h.current_tag_.data_ == expected_parent_data
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == tag
        assert self.h.current_tag_.children_[0].attributes_ == attrs
        assert self.h.current_tag_.children_[0].parent_.name_ == parent_tag

    def test_handle_comment_normal_data(self):
        data = "my data"
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root with comment tag appended to children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == expected_tag
        assert self.h.current_tag_.children_[0].attributes_ == expected_attributes
        assert self.h.current_tag_.children_[0].data_ == data
        assert self.h.current_tag_.children_[0].parent_.name_ == expected_root_tag

    def test_handle_comment_data_with_only_carriage_return_and_newline(self):
        data = "\r\n"
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root no children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 0

    def test_handle_comment_string_with_cr_nl_inside(self):
        data = "my\rdata\ntest"
        expected_data = "mydatatest"
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root with comment tag appended to children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == expected_tag
        assert self.h.current_tag_.children_[0].attributes_ == expected_attributes
        assert self.h.current_tag_.children_[0].data_ == expected_data
        assert self.h.current_tag_.children_[0].parent_.name_ == expected_root_tag

    def test_handle_comment_none_as_data(self):
        data = None
        expected_tag = "comment"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_comment(data)
        # current_tag should still be root with 0 children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 0

    def test_handle_decl_normal_data(self):
        data = "my data"
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root with declaration tag appended to children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == expected_tag
        assert self.h.current_tag_.children_[0].attributes_ == expected_attributes
        assert self.h.current_tag_.children_[0].data_ == data
        assert self.h.current_tag_.children_[0].parent_.name_ == expected_root_tag

    def test_handle_decl_data_with_only_carriage_return_and_newline(self):
        data = "\r\n"
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root no children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 0

    def test_handle_decl_string_with_cr_nl_inside(self):
        data = "my\rdata\ntest"
        expected_data = "mydatatest"
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root with declaration tag appended to children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == expected_tag
        assert self.h.current_tag_.children_[0].attributes_ == expected_attributes
        assert self.h.current_tag_.children_[0].data_ == expected_data
        assert self.h.current_tag_.children_[0].parent_.name_ == expected_root_tag

    def test_handle_decl_none_as_data(self):
        data = None
        expected_tag = "declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.handle_decl(data)
        # current_tag should still be root with 0 children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 0

    def test_unknown_decl_normal_data(self):
        data = "my data"
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root with unknown_declaration tag appended to children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == expected_tag
        assert self.h.current_tag_.children_[0].attributes_ == expected_attributes
        assert self.h.current_tag_.children_[0].data_ == data
        assert self.h.current_tag_.children_[0].parent_.name_ == expected_root_tag

    def test_unknown_decl_data_with_only_carriage_return_and_newline(self):
        data = "\r\n"
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root no children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 0

    def test_unknown_decl_string_with_cr_nl_inside(self):
        data = "my\rdata\ntest"
        expected_data = "mydatatest"
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root with unknown_declaration tag appended to children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 1
        assert self.h.current_tag_.children_[0].name_ == expected_tag
        assert self.h.current_tag_.children_[0].attributes_ == expected_attributes
        assert self.h.current_tag_.children_[0].data_ == expected_data
        assert self.h.current_tag_.children_[0].parent_.name_ == expected_root_tag

    def test_unknown_decl_none_as_data(self):
        data = None
        expected_tag = "unknown_declaration"
        expected_attributes = None
        expected_root_tag = "root"
        expected_root_attributes = None
        expected_root_data = None
        expected_root_parent = None
        self.h.unknown_decl(data)
        # current_tag should still be root with 0 children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.current_tag_.attributes_ == expected_root_attributes
        assert self.h.current_tag_.data_ == expected_root_data
        assert self.h.current_tag_.parent_ == expected_root_parent
        assert len(self.h.current_tag_.children_) == 0

    def test_StoreTag_tag_with_data_but_no_children(self):
        tag_name = "mytag"
        attrs = [('id', 'lga')]
        tag_children = None
        tag_data = "my data"
        tag = HTML.Tag(name=tag_name, attributes=attrs, children=tag_children, data=tag_data)
        self.h.StoreTag(tag)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert len(self.h.parsed_data_) == 1
        assert self.h.parsed_data_[0][0] == tag_name
        assert self.h.parsed_data_[0][1] == attrs
        assert self.h.parsed_data_[0][2] == tag_data

    def test_StoreTag_tag_as_none(self):
        tag = None
        self.h.StoreTag(tag)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert len(self.h.parsed_data_) == 0

    def test_StoreTag_tag_with_data_and_children(self):
        tag_name1 = "mytag1"
        attrs1 = [('id', 'lga')]
        tag_children1 = None
        tag_data1 = "my data1"
        tag1 = HTML.Tag(name=tag_name1, attributes=attrs1, children=tag_children1, data=tag_data1)
        tag_name2 = "mytag2"
        attrs2 = [('id', 'lga')]
        tag_children2 = None
        tag_data2 = "my data2"
        tag2 = HTML.Tag(name=tag_name2, attributes=attrs2, children=tag_children2, data=tag_data2)
        tag_name3 = "mytag3"
        attrs3 = [('id', 'lga')]
        tag_children3 = [tag1, tag2]
        tag_data3 = "my data3"
        tag3 = HTML.Tag(name=tag_name3, attributes=attrs3, children=tag_children3, data=tag_data3)
        self.h.StoreTag(tag3)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert len(self.h.parsed_data_) == 3
        assert self.h.parsed_data_[0][0] == tag_name3
        assert self.h.parsed_data_[0][1] == attrs3
        assert self.h.parsed_data_[0][2] == tag_data3
        assert self.h.parsed_data_[1][0] == tag_name1
        assert self.h.parsed_data_[1][1] == attrs1
        assert self.h.parsed_data_[1][2] == tag_data1
        assert self.h.parsed_data_[2][0] == tag_name2
        assert self.h.parsed_data_[2][1] == attrs2
        assert self.h.parsed_data_[2][2] == tag_data2

    def test_Parse_markup_as_none(self):
        text = None
        expected_result = True
        expected_root_tag = 'root'
        expected_root_children = []
        expected_tag_count = 1
        assert self.h.Parse(text) == expected_result
        assert len(self.h.parsed_data_) == expected_tag_count
        assert self.h.parsed_data_[0][0] == expected_root_tag
        assert self.h.root_.name_ == expected_root_tag
        assert self.h.root_.children_ == expected_root_children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.number_of_tags_ == expected_tag_count

    def test_Parse_good_html_with_several_tags(self):
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
        assert self.h.Parse(text) == expected_result
        assert self.h.root_.name_ == expected_root_tag
        assert len(self.h.root_.children_) == expected_root_children
        assert self.h.number_of_tags_ == expected_tag_count
        assert len(self.h.parsed_data_) == expected_tag_count
        assert self.h.parsed_data_[0][0] == expected_root_tag
        assert self.h.parsed_data_[1][0] == expected_tag_name1
        assert self.h.parsed_data_[1][2] == expected_tag_data1
        assert self.h.parsed_data_[2][0] == expected_tag_name2
        assert self.h.parsed_data_[2][2] == expected_tag_data2
        assert self.h.parsed_data_[3][0] == expected_tag_name3

    def test_Parse_bad_html(self):
        text = "<P><A NAME='anchor'</a></P>"
        expected_result = False
        expected_root_tag = 'root'
        expected_root_children = []
        expected_tag_count = 1
        assert self.h.Parse(text) == expected_result
        #assert len(self.h.parsed_data_) == expected_tag_count
        #assert self.h.parsed_data_[0][0] == expected_root_tag
        assert self.h.root_.name_ == expected_root_tag
        assert self.h.root_.children_ == expected_root_children
        assert self.h.current_tag_.name_ == expected_root_tag
        assert self.h.number_of_tags_ == expected_tag_count

    def test_ParseFile_html_file_as_input(self):
        filename = "test.html"
        expected_result = True
        assert self.h.ParseFile(filename) == expected_result

    def test_ParseFile_non_existant_file(self):
        filename = "invalid_file.html"
        expected_result = False
        assert self.h.ParseFile(filename) == expected_result

    def test_ParseFile_none_as_filename(self):
        filename = None
        expected_result = False
        assert self.h.ParseFile(filename) == expected_result

    def test_ParseURL_google_as_input(self):
        url = "http://www.google.com"
        expected_result = True
        assert self.h.ParseURL(url) == expected_result

    def test_ParseURL_non_existant_url(self):
        url = "http://asdf1974jgladslf.com"
        expected_result = False
        assert self.h.ParseURL(url) == expected_result

    def test_ParseURL_none_as_url(self):
        url = None
        expected_result = False
        assert self.h.ParseURL(url) == expected_result

# FindFirstTag(type, attr, data)
    def test_FindFirstTag_all_inputs_none(self):
        type = None
        attr = None
        data = None
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_tag_type_not_found(self):
        type = "aaaaaaaaa"
        attr = None
        data = None
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match(self):
        type = "d"
        attr = None
        data = None
        expected_result = 2
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_one_attribute_missing(self):
        type = "abc"
        attr = [('id', 'lga')]
        data = None
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_one_attribute_not_equal(self):
        type = "abc"
        attr = [('id', 'lga'), ('xy', 'a')]
        data = None
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_attribute_match(self):
        type = "abc"
        attr = [('id', 'lga'), ('xy', 'z')]
        data = None
        expected_result = 1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_data_mismatch(self):
        type = "abc"
        attr = None
        data = "asdf"
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_data_match(self):
        type = "abc"
        attr = None
        data = "data1"
        expected_result = 1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_attributes_match_data_mismatch(self):
        type = "xyz"
        attr = [('id', 'lga'), ('xy', 'z')]
        data = "dddddddd"
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_type_match_attributes_mismatch_data_match(self):
        type = "xyz"
        attr = [('id', 'hhh'), ('xy', 'z')]
        data = "data2"
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindFirstTag_everything_matches(self):
        type = "d"
        attr = [('id', '2'), ('xy', 'w')]
        data = "data4"
        expected_result = 3
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindFirstTag(type, attr, data) == expected_result

    def test_FindNextTag_type_match(self):
        type = "d"
        attr = None
        data = None
        index = 3
        expected_result = 3
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '2'), ('xy', 'w')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindNextTag(type, attr, data, index) == expected_result

    def test_FindNextTag_type_and_attribute_match(self):
        type = "d"
        attr = [('id', '1'), ('xy', 'z')]
        data = None
        index = 3
        expected_result = 3
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindNextTag(type, attr, data, index) == expected_result

    def test_FindNextTag_no_more_matching_tags(self):
        type = "abc"
        attr = None
        data = None
        index = 2
        expected_result = -1
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.FindNextTag(type, attr, data, index) == expected_result

    def test_GetTag_negative_index(self):
        index = -1
        expected_result = None
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.GetTag(index) == expected_result

    def test_GetTag_index_greater_than_tag_count(self):
        index = 500
        expected_result = None
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.GetTag(index) == expected_result

    def test_GetTag_index_equal_to_tag_count(self):
        index = 4
        expected_result = None
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = HTML.Tag(name="xyz", attributes=[('id', 'lga'), ('xy', 'z')], children=[tag1, tag3, tag4], data="data2")
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        assert self.h.GetTag(index) == expected_result

    def test_GetTag_valid_index(self):
        index = 0
        expected_name = "xyz"
        expected_attributes = [('id', 'lga'), ('xy', 'z')]
        expected_data = "data2"
        # Preconditions
        tag1 = HTML.Tag(name="abc", attributes=[('id', 'lga'), ('xy', 'z')], children=None, data="data1")
        tag3 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data3")
        tag4 = HTML.Tag(name="d", attributes=[('id', '1'), ('xy', 'z')], children=None, data="data4")
        tag2 = HTML.Tag(name=expected_name, attributes=expected_attributes, children=[tag1, tag3, tag4], data=expected_data)
        self.h.StoreTag(tag2)
        self.h.number_of_tags_ = len(self.h.parsed_data_)
        newtag = self.h.GetTag(index)
        assert newtag[0] == expected_name
        assert newtag[1] == expected_attributes
        assert newtag[2] == expected_data

