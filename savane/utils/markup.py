# Savane3 custom markup system
# Copyright (C)  2005, 2006  Tobias Toedter
# Copyright (C)  2005, 2006  Mathieu Roy
# Copyright (C)  2010  Sylvain Beucler
# 
# This file is part of Savane.
#
# Savane is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Savane is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# The goal is to provide a syntax compatible with Savane 3.  The
# original implementation uses a line-based parsers with a few issues
# (e.g. when using \n instead of \r\n).  I (Beuc) think a cleaner
# implementation would use a tokeniser and a grammar - and would
# otherwise reuse an existing syntax rather than create yet another
# one.  We keep it for backward compatibility.  I think we should not
# improve it and rather add support for an existing syntax (one of
# reStructuredText, MediaWiki...).

## Provides functions to allow users to format the text in a secure way:
##    basic() for very light formatting
##    rich() for formatting excepting headers
##    full() for full formatting, including headers

from django.conf import settings
from xml.sax.saxutils import quoteattr
import re

def info(level):
    """
    Will tell the user what is the level of markup available in a
    uniformized way.
    Takes as argument the level, being full / rich / basic / none
    To avoid making page looking strange, we will put that only on textarea
    where it is supposed to be the most useful
    """
    if level == 'basic':
        string = _("Basic markup")
        text = _("Only basic text tags are available in this input field.")
    elif level == 'rich':
        string = _("Rich markup")
        text = _("Rich and basic text tags are available in this input field.")      
    elif level == 'full':
        string = _("Full markup")
        text = _("Every tags are available in this input field.")      
    elif level == 'none':
        string = _("No markup")
        text = _("No tags are available in this input field.")    

    if level != 'none':
        text = text + " " + _("Check the markup reminder in related documentation for a description of these tags.")

    return '<span class="help" title=' + quoteattr(text) \
        + '><img src="' + settings.STATIC_MEDIA_URL \
        + 'images/savane/common/misc.default/edit.png' \
        + ' border="0" class="icon" alt="" />' \
        + string + '</span>'

def basic(text):
    r"""
    Converts special markup characters in the input text to real HTML
    
    The following syntax is supported:
    *word* -> <strong>word</strong>
    _word_ -> <em>word</em>
    [http://savane-forge.org/] -> <a href="http://savane-forge.org/">http://savane-forge.org/</a>
    [http://savane-forge.org/ text] -> <a href="http://savane-forge.org/">text</a>
    [disabled] (bug|task|...) #1234 -> Link to corresponding page

    >>> basic('*word*')
    '<strong>word</strong>'
    >>> basic("*word\n*")
    '*word\n*'
    >>> basic('_word_')
    '<em>word</em>'
    >>> basic('_wo\nrd_')
    '_wo\nrd_'
    >>> basic('[http://savane-forge.org/]')
    '<a href="http://savane-forge.org/">http://savane-forge.org/</a>'
    >>> basic('[http://savane-forge.org/ text]')
    '<a href="http://savane-forge.org/">text</a>'
    """
    lines = text.split("\n")
    result = []

    for line in lines:
        result.append(_inline(line))

    return "\n".join(result)

def rich(text):
    r"""
    Converts special markup characters in the input text to real HTML
    
    This function does the same markup as basic(), plus
    it supports the following:
    * paragraphs
    * lists (<ul> and <ol>)
    * nested lists
    * horizontal rulers

    >>> rich("A\nB")
    '<p>A<br />\nB<br />\n</p>'
    >>> rich("A\n\nB")
    '<p>A<br />\n</p>\n<p>B<br />\n</p>'
    >>> rich("* A")
    '<ul>\n<li>A\n</li>\n</ul>'
    >>> rich("* A\n** A.1\n** A.2\n* 2\n")
    '<ul>\n<li>A\n<ul>\n<li>A.1\n</li>\n<li>A.2\n</li>\n</ul>\n</li>\n<li>2\n</li>\n</ul>'
    >>> rich("0 A\n0* A.1\n0 2")
    '<ol>\n<li>A\n<ul>\n<li>A.1\n</li>\n</ul>\n</li>\n<li>2\n</li>\n</ol>'
    >>> rich("* A\n0 B\n* C")
    '<ul>\n<li>A\n</li>\n</ul><ol>\n<li>B\n</li>\n</ol><ul>\n<li>C\n</li>\n</ul>'
    >>> rich("----")
    '<hr />'
    >>> rich("+verbatim+\n  indented_code();\n-verbatim-")
    '<input type="text" class="verbatim" readonly="readonly" size="60" value="  indented_code();" />'
    >>> rich("+verbatim+\n1\r\n2\n-verbatim-")
    '<textarea class="verbatim" readonly="readonly" rows="2" cols="80">1\r2</textarea>'
    >>> rich("+nomarkup+\n_word_\n*word*\n-nomarkup-")
    '<p><br />\n_word_<br />\n*word*<br />\n<br />\n</p>'
    >>> rich("+verbatim+\n+nomarkup+\n-verbatim-")
    '<input type="text" class="verbatim" readonly="readonly" size="60" value="+nomarkup+" />'
    """
    return full(text, False)

def full(text, allow_headings=True):
    r"""
    Converts special markup characters in the input text to real HTML
    
    This function does the same markup as rich(), plus
    it converts headings to <h3> ... <h6>

    >>> full('= A =')
    '<h2>A</h2>'
    >>> full('== A ==')
    '<h3>A</h3>'
    >>> full('=== A ===')
    '<h4>A</h4>'
    >>> full('==== A ====')
    '<h5>A</h5>'
    >>> full('= A =\n=== B ===')
    '<h2>A</h2>\n<h4>B</h4>'
    >>> full('= A =\n\nintro\n\n== B ==')
    '<h2>A</h2>\n\n<p>intro<br />\n</p>\n<h3>B</h3>'
    """
    lines = text.split("\n")
    result = []
    printer = False  # used to be global var in PHP

    # we use a stack (last in, first out) to track the current
    # context (paragraph, lists) so we can correctly close tags
    context_stack = []

    quoted_text = False
    verbatim = False

    for index,line in enumerate(lines):
        # the verbatim tags are not allowed to be nested, because
        # they are translated to HTML <textarea> (<pre> in printer mode),
        # which in turn is also
        # not allowed to be nested.
        # therefore, we dont need a counter of the level, but
        # a simple bool flag
        # We also need to bufferize the verbatim content, as we want to now
        # its exact number of lines
        #
        # yeupou, 2006-10-31: we need a verbatim count, because actually 
        # we may want to put at least one verbatim block into another, for
        # instance in the recipe that explain the verbatim tag
        if re.match('[+]verbatim[+]', line) and not verbatim:
            verbatim = 1
            verbatim_buffer = ''
            verbatim_buffer_linecount = 0

            line = "\n".join(context_stack)

            if not printer:
                context_stack.insert(0, '</textarea>')
            else:
                context_stack.insert(0, '</pre>')

            # Jump to the next line, assuming that we can ignore the rest of the
            # line
            continue

        # Increment the verbatim count if we find a verbatim closing in a 
        # verbatim environment
        if re.match('[+]verbatim[+]', line) and not verbatim:
            verbatim += 1

        if re.match('-verbatim-', line) and verbatim == 1:
            verbatim = False

            line = "\n".join(context_stack)
            context_stack.pop(0)

            #array_pop($result); # no longer useful since we bufferize verbatim
            if not printer:
                # Limit the textarea to 20 lines
                if verbatim_buffer_linecount > 20:
                    verbatim_buffer_linecount = 20

                # Use a text input if it is not multiline
                if verbatim_buffer_linecount < 2:
                    result.append('<input type="text" class="verbatim" readonly="readonly" size="60" value="' \
                                      + verbatim_buffer \
                                      + '" />')
                else:
                    result.append('<textarea class="verbatim" readonly="readonly" rows="' \
                                      + str(verbatim_buffer_linecount) + '" cols="80">' \
                                      + verbatim_buffer + '</textarea>')
            else:
                result.append('<pre class="verbatim">' + verbatim_buffer + '</pre>')
            verbatim_buffer = ''
            verbatim_buffer_linecount = 0
	  
            # Jump to the next line, assuming that we can ignore the
            # rest of the line
            continue

        # Decrement the verbatim count if we find a verbatim closing in a 
        # verbatim environment
        if re.search('-verbatim-', line) and verbatim > 1:
            verbatim -= 1

        # if we're in the verbatim markup, don't apply the markup
        if verbatim:
            # disable the +nomarkup+ tags by inserting a unique string.
            # this has to be done in the original string, because that
            # is the one which will be split upon the +nomarkup+ tags,
            # see below
            escaped_line = line.replace('nomarkup', 'no-1a4f67a7-4eae-4aa1-a2ef-eecd8af6a997-markup')
            lines[index] = escaped_line;
            verbatim_buffer += escaped_line;
            verbatim_buffer_linecount += 1
        else:
            # Otherwise, normal run, do the markup
            (line, context_stack, quoted_text) = _full_markup(line, allow_headings, context_stack, quoted_text)
            result.append(line)

    # make sure that all previously used contexts get their
    # proper closing tag by merging in the last closing tags
    markup_text = "\n".join(result + context_stack)

    # its easiest to markup everything, without supporting the nomarkup
    # tag. afterwards, we replace every nomarkup tag pair with the content
    # between those tags in the original string
    # keep the '()' in the regexp's so the matched tag is part of the result
    original = re.split('([+-]nomarkup[+-])', "\n".join(lines))
    markup = re.split('([+-]nomarkup[+-])', markup_text)
    # save the HTML tags from the last element in the markup array, see below
    last_tags = markup[len(markup)-1]
    nomarkup_level = 0

    for index,original_text in enumerate(original):
        # keep track of nomarkup tags
        if original_text == '+nomarkup+': nomarkup_level += 1
        if original_text == '-nomarkup-': nomarkup_level -= 1

        # if the current match is the nomarkup tag, we don't want it to
        # show up in the markup text -> set it to an empty string
        if re.search('[+-]nomarkup[+-]', original_text):
            markup[index] = ''
            original_text = ''

        # while we're in a nomarkup environment, the already marked up text
        # needs to be replaced with the original content. Also, we need
        # to add <br />  tags for newlines.
        if nomarkup_level > 0:
            markup[index] = original_text.replace('\n','<br />\n')

    # normally, $nomarkup_level must be zero at this point. however, if
    # the user submits wrong markup and forgets to close the -nomarkup-
    # tag, we need to take care of that.
    # To do this, we need to look for closing tags which have been deleted.
    if nomarkup_level > 0:
        trailing_markup = last_tags.split('\n')[::-1]
        restored_tags = ''

        for tag in trailing_markup:
            if re.match('^\s*<\/[a-z]+>$', tag):
                restored_tags = "\n" + tag + restored_tags
            else:
                markup.append(restored_tags)
                break

    # lastly, revert the escaping of +nomarkup+ tags done above
    # for verbatim environments
    return ''.join(markup).replace('no-1a4f67a7-4eae-4aa1-a2ef-eecd8af6a997-markup', 'nomarkup')

def textoutput(text):
    r"""
    Convert whatever content that can contain markup to a valid text output
    It wont touch what seems to be valid in text already, or what cannot
    be converted in a very satisfactory way.
    This function should be minimal, just to avoid weird things, not to do
    very fancy things.

    >>> textoutput('[http://savane-forge.org/ Link]')
    'Link <http://savane-forge.org/>'
    >>> textoutput('[http://savane-forge.org/]')
    '[http://savane-forge.org/]'
    >>> textoutput('a\n-verbatim-\nb')
    'a\n\nb'
    >>> textoutput('a\n+nomarkup+\nb')
    'a\n\nb'
    """

    lines = text.split("\n")
    result = []

    protocols = "https?|ftp|sftp|file|afs|nfs"
    savane_tags = "verbatim|nomarkup"

    for line in lines:
        # Handle named hyperlink.
        line = re.sub(
              # find the opening brace '['
		     '\['
              # followed by the protocol, either http:// or https://
		     + '((' + protocols + '):\/\/'
              # match any character except whitespace or the closing
              # brace ']' for the actual link
		     + '[^\s\]]+)'
              # followed by at least one whitespace
		     + '\s+'
              # followed by any character (non-greedy) and the
              # next closing brace ']'
		     + '(.+?)\]', '\\3 <\\1>', line)
      
        # Remove savane-specific tags
        line = re.sub('\+(' + savane_tags + ')\+', '', line)
        line = re.sub('-(' + savane_tags + ')-', '', line)
        result.append(line)

    return "\n".join(result)

def _full_markup(line, allow_headings, context_stack, quoted_text):
    """
    Internal function for recognizing and formatting special markup
    characters in the input line to real HTML

    This function is a helper for utils_full_markup() and should
    not be used otherwise.
    """

    #############################################################
    # context formatting
    #
    # the code below marks up recognized special characters,
    # by starting a new context (e.g. headings and lists)
    #############################################################

    # generally, we want to start a new paragraph. this will be set
    # to false, if a new paragraph is no longer appropriate, like
    # for headings or lists
    start_paragraph = True

    # Match the headings, e.g. === heading ===
    if allow_headings:
        (line, context_stack, start_paragraph) = _headings(line, context_stack, start_paragraph)

    # Match list items
    (line, context_stack, start_paragraph) = _lists(line, context_stack, start_paragraph)

    # replace four '-' sign with a horizontal ruler
    if re.match('^----\s*$', line):
        line = "\n".join(context_stack) + '<hr />'
        context_stack = []
        start_paragraph = False

    ############################################################
    # inline formatting
    #
    # the code below marks up recognized special characters,
    # without starting a new context (e.g. <strong> and <em>)
    #############################################################

    line = _inline(line)

    #############################################################
    # paragraph formatting
    #
    # the code below is responsible for doing the Right Thing(tm)
    # by either starting a new paragraph and closing any previous
    # context or continuing an existing paragraph
    #############################################################

    # change the quoteing mode when the line start with '>'
    if line[0:4] == '&gt;':
        # if the previous line was not quoted, start a new quote paragraph
        if not quoted_text:
            line = "\n".join(context_stack) + "<p class=\"quote\">" + line
            # empty the stack
            context_stack = ['</p>']
            start_paragraph = False
        quoted_text = True
    else:
        # if the previous line was quoted, end the quote paragraph
        if quoted_text and start_paragraph and line != '':
            line = "\n".join(context_stack) + "\n<p>" + line
            # empty the stack
            context_stack = ['</p>']
        quoted_text = False

    # don't start a new paragraph again, if we already did that
    if len(context_stack) > 0 and context_stack[0] == '</p>':
        start_paragraph = False

    # add proper closing tags when we encounter an empty line.
    # note that there might be no closing tags, in this case
    # the line will remain emtpy.
    if re.match('^(|\s*)$', line):
        line = "\n".join(context_stack) + line
        # empty the stack
        context_stack = []
        start_paragraph = False

    # Finally start a new paragraph if appropriate
    if start_paragraph:
        # make sure that all previously used contexts get their
        # proper closing tag
        line = "\n".join(context_stack) + "<p>" + line
        # empty the stack
        context_stack = ['</p>']

    # append a linebreak while in paragraph mode
    if len(context_stack) > 0 and context_stack[0] == '</p>':
        line += '<br />'

    return (line, context_stack, quoted_text)

def _headings(line, context_stack, start_paragraph):
    """
    Internal function for recognizing and formatting headings
    
    This function is a helper for _full_markup() and should
    not be used otherwise.
    """
    matches = re.search(
        # find one to four '=' signs at the start of a line
        '^(={1,4})'
        # followed by exactly one space
        + ' '
        # followed by any character
        + '(.+)'
        # followed by exactly one space
        + ' '
        # followed by one to four '=' signs at the end of a line (whitespace allowed)
        + '(={1,4})\s*$', line)
    if matches:
        header_level_start = max(min(len(matches.group(1)), 4), 1)
        header_level_end = len(matches.group(3))
        if header_level_start == header_level_end:
            # if the user types '= heading =' (one '=' sign), it will
            # actually be rendered as a level 2 heading <h2>
            header_level_start += 1
            header_level_end += 1

            line = ("<h" + str(header_level_start) + ">"
                    + matches.group(2)
                    + "</h" + str(header_level_end) + ">")
            # make sure that all previously used contexts get their
            # proper closing tag
            line = "\n".join(context_stack) + line
            # empty the stack
            context_stack = []
            start_paragraph = False
    return (line, context_stack, start_paragraph)

def _lists(line, context_stack, start_paragraph):
    """
    Internal function for recognizing and formatting lists
    
    This function is a helper for _full_markup() and should
    not be used otherwise.
    """
    matches = re.search('^\s?([*0]+) (.+)$', line)
    if matches is not None:
        # determine the list level currently in use
        current_list_level = 0
        for context in context_stack:
            if context == '</ul>' or context == '</ol>':
                current_list_level += 1

        # determine whether the user list levels match the list
        # level we have in our context stack
        #
        # this will catch (potential) errors of the following form:
        # * list start
        # 0 maybe wrong list character
        # * list end
        markup_position = 0
        for context in context_stack[::-1]:
            # we only care for the list types
            if context != '</ul>' and context != '</ol>':
                continue
    
            markup_character = matches.group(1)[markup_position:markup_position+1]
    
            if ((markup_character == '*' and context != '</ul>')
                or (markup_character == '0' and context != '</ol>')):
                # force a new and clean list start
                current_list_level = 0
                break
            else:
                markup_position += 1
    
        # if we are not in a list, close the previous context
        line = ''
        if current_list_level == 0:
            line = "\n".join(context_stack)
            context_stack = []
    
        # determine the list level the user wanted
        wanted_list_level = len(matches.group(1))
    
        # here we start a new list and make sure that the markup
        # is valid, even if the user did skip one or more list levels
        list_level_counter = current_list_level
        while list_level_counter < wanted_list_level:
            test = matches.group(1)[list_level_counter:list_level_counter+1]
            if test == '*':
                tag = 'ul'
            elif test == '0':
                tag = 'ol'
            line += "<" + tag + ">\n<li>"
            context_stack.insert(0, "</"+ tag + ">")
            context_stack.insert(0, "</li>")
            list_level_counter += 1

        # here we end a previous list and make sure that the markup
        # is valid, even if the user did skip one or more list levels
        list_level_counter = current_list_level
        while list_level_counter > wanted_list_level:
            line += context_stack.pop(0) + "\n" \
                + context_stack.pop(0) + "\n"
            list_level_counter -= 1

        # prepare the next item of the same list level
        if current_list_level >= wanted_list_level:
            line += "</li>\n<li>"

        # finally, append the list item
        line += matches.group(2)
        start_paragraph = False

    return (line, context_stack, start_paragraph)

def _inline(line):
    """
    Internal function for recognizing and formatting inline tags and links
    
    This function is a helper for _full_markup() and should not be
    used otherwise.
    """
    if len(line) == 0:
        return ''

    # Regexp of protocols supported in hyperlinks (should be protocols that
    # we can expect web browsers to support)
    protocols = "https?|ftp|sftp|file|afs|nfs"


    # Prepare usual links: prefix every "www." with "http://"
    # unless there is a // before
    line = re.sub('(^|\s|[^\/])(www\.)', '\\1http://\\2', line, re.I);

    # replace the @ sign with an HTML entity, if it is used within
    # an url (e.g. for pointers to mailing lists). This way, the
    # @ sign doesn't get mangled in the e-mail markup code
    # below. See bug #2689 on http://gna.org/ for reference.
    line = re.sub("([a-z]+://[^<>[:space:]]+)@", "\\1&#64;", line, re.I)

    # Prepare the markup for normal links, e.g. http://test.org, by
    # surrounding them with braces []
    # (& = begin of html entities, it means a end of string unless
    # it is &amp; which itself is the entity for &)
    line = re.sub('(^|\s|[^\[])((' + protocols + '):\/\/(&amp;|[^\s&]+[a-z0-9\/^])+)',
                  '\\1[\\2]', line, re.I)

    # do a markup for mail links, e.g. info@support.org
    # (do not use utils_emails, this does extensive database
    # search on the string
    # and replace addresses in several fashion. Here we just want to make
    # a link). Make sure that 'cvs -d:pserver:anonymous@cvs.sv.gnu.org:/...'
    # is NOT replaced.
    line = re.sub("(^|\s)([a-z0-9_+-.]+@([a-z0-9_+-]+\.)+[a-z]+)(\s|$)",
                  '\\1' + '<a href="mailto:\\2">\\2</a>' + '\\4', line, re.I)

    # Links between items
    # FIXME: it should be i18n, but in a clever way, meaning that everytime
    # a form is submitted with such string, the string get converted in
    # english so we always get the links found without having a regexp
    # including every possible language.
    # Trackers URLs disabled until trackers are actually implemented :)
    #trackers = {
    #    "bugs?" : "bugs/?",
    #    "support|sr" : "support/?",
    #    "tasks?" : "task/?",
    #    "patch" : "patch/?",
    #    # In this case, we make the link pointing to support, it wont matter,
    #    # the download page is in every tracker and does not check if the tracker
    #    # is actually used
    #    "files?" : "support/download.php?file_id=",
    #    }
    #for regexp,link in trackers:
    #    # Allows only two white space between the string and the numeric id
    #    # to avoid having too time consuming regexp. People just have to pay
    #    # attention.
    #    line = re.sub("(^|\s|\W)($regexp)\s{0,2}#([0-9]+)",
    #                  '\1<em><a href="' + 'sys_home'
    #                  + link + '\\3">\\2&nbsp;#\\3</a></em>',
    #                  line, re.I)

    # add an internal link for comments
    line = re.sub('(comments?)\s{0,2}#([0-9]+)',
                  '<em><a href="#comment\\2">\\1&nbsp;#\\2</a></em>',
                  line, re.I)

    # Add support for named hyperlinks, e.g.
    # [http://savane-forge.org/ Text] -> <a href="http://savane-forge.org/">Text</a>
    line = re.sub(
        # find the opening brace '['
        '\['
        # followed by the protocol, either http:// or https://
        + '((' + protocols + '):\/\/'
        # match any character except whitespace or the closing
        # brace ']' for the actual link
        + '[^\s\]]+)'
        # followed by at least one whitespace
        + '\s+'
        # followed by any character (non-greedy) and the
        # next closing brace ']'
        + '(.+?)\]',
        '<a href="\\1">\\3</a>', line)

    # Add support for unnamed hyperlinks, e.g.
    # [http://savane-forge.org/] -> <a href="http://savane-forge.org/">http://savane-forge.org/</a> 
    line = re.sub(
        # find the opening brace '['
        '\['
        # followed by the protocol, either http:// or https://
        # (FIXME: which protocol does it makes sense to support, which one
        # should we ignore?)
        + '((' + protocols + '):\/\/'
        # match any character except whitespace (non-greedy) for
        # the actual link, followed by the closing brace ']'
        + '[^\s]+?)\]',
        '<a href="\\1">\\1</a>', line)

    # *word* -> <strong>word</strong>
    line = re.sub(
        # find an asterisk
        '\*'
        # then one character (except a space or asterisk)
        + '([^* ]'
        # then (optionally) any character except asterisk
        + '[^*]*?)'
        # then an asterisk
        + '\*',
        '<strong>\\1</strong>', line)

    # _word_ -> <em>word</em>
    line = re.sub(
        # allow for the pattern to start at the beginning of a line.
        # if it doesn't start there, the character before the slash
        # must be either whitespace or the closing brace '>', to
        # allow for nested html tags (e.g. <p>_markup_</p>).
        # Additionally, the opening brace may appear.
        # See bug #10571 on http://gna.org/ for reference.
        '(^|\s+|>|\()'
        # match the underscore
        + '_'
        # match any character (non-greedy)
        + '(.+?)'
        # match the ending underscore and either end of line or
        # a non-word character
        + '_(\W|$)',
        '\\1<em>\\2</em>\\3',
        line)

    return line

if __name__ == "__main__":
    import doctest
    doctest.testmod()
