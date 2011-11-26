# GVCommander #

Introduction
------------

This is a more direct GV-to-GTalk service that polls Google Voice servers for
new message (yay for shameless HTML scraping!) and then forwards it to a 
specified GTalk account. It also receives messages from GTalk and creates the
corresponding SMS to the appropriate person. This eliminates the need to 
re-route messages through email, which is slower and more error-prone. 

Also, this is completely open-source (GPLv3). Feel free to modify it and 
redistribute it as you wish so long as you cite back the original source.

Dependencies
------------

This project could not be possibly without the wonderful work of 
[PyGoogleVoice](http://www.code.google.com/p/pygooglevoice/), [xmpppy](http://www.xmpppy.sourceforge.net), 
and [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/). 

This code is bundled with a very stripped-down version of PyGoogleVoice as well 
as xmppy. You will need to have BeautifulSoup to run this.

**This code is written in Python 2.7.**

## WARNING ##

**At this stage, this code is VERY buggy. Expect it to break every vase you 
own and individually offend each person on your contact list. Use at your own
risk (okay, it isn't that bad..).**
