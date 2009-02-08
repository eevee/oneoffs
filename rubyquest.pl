#!/usr/bin/perl
# The very definition of a oneshot; I wanted to combine RubyQuest into a single
# page with the 4chan clutter removed, which only needs doing once!
# I scraped a list of thread archive links from the tagged list in the link
# below, put them in a file, and fed that to wget, which is why the files are
# all named index.html.\d+.

# Some header crap
print <<'END';
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<link rel="stylesheet" href="http://stuff.veekun.com/reset.css"/>
<style type="text/css">
    body { margin: 1em; }
    #title { font-size: 3em; margin-bottom: 0.33em; font-weight: bold; color: #c00000; }
    #top { font-size: 0.75em; font-style: italic; }
    h1 { font-size: 2em; padding-top: 0.5em; margin-top: 0.5em; border-top: 3px double black; font-weight: bold; }
    .panel { overflow: hidden; margin: 1em 0; padding-top: 1em; border-top: 1px dotted #999; }
    h1 + .panel { border-top: none; }
    .panel > a { display: block; margin-right: 1em; float: left; }
    q { color: #8080a8; font-style: italic; }
</style>
</head>
<body>
<div id="title">RubyQuest</div>
<p id="top">Thread archives from <a href="http://4chan.thisisnotatrueending.com/archive.html?tags=Ruby">sup/tg/</a>.  Also contains lots of discussion and fanart threads.</p>
END

@ARGV = ('index.html', map { "index.html.$_" } 1 .. 30);

# For tracking the current part
my $last_argv = '';
my $cur_part = 0;

# For tracking the current thread id
my $thread_id = '???';

while (<>) {
    if (m{<input [^>]+ name="?resto"? [^>]+ value="(\d+)"}x) {
        # No idea what this does, but it's the thread id, which we need for images
        $thread_id = $1;
        next;
    }

    # First post is split across several lines
    if (m{<form.+delform}) {
        # Image is on this line, but the <blockquote> is three lines down
        for my $n (1 .. 3) {
            $_ .= <>;
        }
    }
        
    # Skip every line not containing Weaver's tripcodes
    next if not m{ class="postertrip" > !!(?:vY8rj3XdjnI|t1PjjQn4qVX)< }x;

    # Extract text and image filename
    my ($text) = m{ <blockquote>(.+)</blockquote> }x;
    my ($img, $thumb) = m{ <a \s href="?((?:images/)?\d+\.\w+)"? [^>]+ ><img [^>]+ src="?((?:thumbs/)?\d+s\.\w+)"? }x;

    # Bail?
    # Bail.
    next if not $text and not $img;

    ### Clean up text
    # Remove links to other posts because who cares
    $text =~ s{<font class="unkfunc"><a[^>]+class="quotelink"[^>]+>&gt;&gt;\d+</a></font><br ?/?>}{}g;
    # Make <font> tags into css because wtf
    $text =~ s{<font class="unkfunc">}{<q>}g;
    $text =~ s{</font>}{</q>}g;
    # Better <br>s I guess eh
    $text =~ s{<br ?/?>}{<br/>\n        }g;

    # Print header if this is a new page
    if ($last_argv ne $ARGV) {
        warn $ARGV;
        $cur_part++;
        print qq{<h1>Part $cur_part</h1>\n};
        $last_argv = $ARGV;
    }

    print qq{<div class="panel">\n};
    if ($img) {
        print qq{    <a href="http://4chan.thisisnotatrueending.com/archive/$thread_id/$img">\n};
        print qq{        <img src="http://4chan.thisisnotatrueending.com/archive/$thread_id/$thumb" alt=""/>\n};
        print qq{    </a>\n};
    }
    print qq{    <p>\n};
    print qq{        $text\n};
    print qq{    </p>\n};
    print qq{</div>\n};
}

# "Footer"
print <<'END'
</body>
</html>
END
