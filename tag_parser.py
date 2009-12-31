#!/usr/bin/env python
"""Dead-simple parser for a simple example language with nested tags, like
HTML.

Written to demonstrate to someone how to parse such a language in one pass and
without recursion.

In its current state, this is not very useful: it will only recognize {...} as
a construct.  Should be easy to extend, though.

Takes a single argument, the string to pass, and prints a parse tree.
"""

from cStringIO import StringIO
import sys

string = sys.argv[1]

# At any given time, the context contains every open tag that contains our
# current position.  For example, while parsing the 'bar' above, the context
# should contain two '{' frames.
context = []

# Each node is a list of (type, contents) tuples.  We start off with a single
# empty node, representing an empty document.
nodes = [ [] ]

buf = buffer(string)
for ch in buf:
    if ch == '{':
        # New child node.  Add it to our context
        context.append(ch)
        nodes.append([])

    elif ch == '}':
        # Closing a node.  Pop our stacks and combine our current node with
        # its parent
        if not len(context):
            raise ValueError('Unopened tag')

        matching_tag = context.pop()
        if matching_tag != '{':
            raise ValueError('Mismatched tags')

        # The last node needs a new element containing the type, 'BRACE', and
        # its contents, which we accumulated in the current node
        current_node = nodes.pop()
        nodes[-1].append( ('BRACE', current_node) )

    else:
        # This is any text.  If the last element in the current node isn't
        # TEXT, create a new one.  Then append this character.
        # I use a string buffer to make appending quick and easy.
        # Caveat emptor: you will wind up with a tree full of string buffers,
        # not strings!  Resolving this is left as an exercise for the reader.
        if len(nodes[-1]) == 0 or nodes[-1][-1][0] != 'TEXT':
            nodes[-1].append( ('TEXT', StringIO()) )

        nodes[-1][-1][1].write(ch)

# Should only be one node remaining
if len(nodes) > 1:
    raise ValueError('Unclosed tag')

tree = nodes[-1]


def print_node(node, indent=0):
    for type, contents in node:
        print ' ' * indent, type, ':',
        if isinstance(contents, list):
            print
            print_node(contents, indent + 4)
        else:
            print contents.getvalue()

print_node(tree)
