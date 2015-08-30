#!/usr/bin/env python

import re
import json
import os
import random
import re
import string
import sys
import tweepy

UNICODE_POO = u"\U0001F4A9"

def space_indices(text):
  return [i for i, x in enumerate(text) if x == u' ']

def mangle_status(text, sender):
  chars = list(text)
  candidate_indices = space_indices(chars)
  idx = random.choice(candidate_indices)
  chars[idx] = UNICODE_POO
  result = u''.join(chars)
  return u'%s\n@%s' % (result, sender)

class TinySpacePooListener(tweepy.StreamListener):
  def __init__(self, api):
    tweepy.StreamListener.__init__(self)
    self.api = api
    # self.status_mangler = StatusMangler()

  def on_status(self, status): #, tweet_id):
    print >> sys.stderr, u"Received tweet author:'%s' text:'%s' id:%d" % (status.author.screen_name.lower(), status.text, status.id)
    # Caution - only retweet the pope, in case other stuff shows up in my stream
    if status.author.screen_name.lower() in (u'tiny_star_field', u'futuresnark'):
      print >> sys.stderr, "Matched user"
      mangled_status = mangle_status(status.text, status.author.screen_name)
      if mangled_status:
        print >> sys.stderr, u"Status mangled:'%s'" % mangled_status
        self.api.update_status(status=mangled_status, in_reply_to_status_id=status.id)
    return True

  def on_error(self, status_code):
    print >> sys.stderr, 'Encountered error with status code:', status_code
    return True # Don't kill the stream

  def on_timeout(self):
    print >> sys.stderr, 'Timeout...'
    return True # Don't kill the stream

def get_creds():
  with open("creds", "r") as f:
    return [line.strip() for line in f]

def get_auth_api():
  k, s1, t, s2 = get_creds()
  auth = tweepy.OAuthHandler(k, s1)
  auth.set_access_token(t, s2)
  return [auth, tweepy.API(auth)]

def main(argv = sys.argv):
  print >> sys.stderr, "Starting"
  auth, api = get_auth_api()
  listener = TinySpacePooListener(api)
  stream = tweepy.Stream(auth, listener, timeout = 3600)

  print >> sys.stderr, "Created stream. Calling userstream()."

  while True:
    try:
      stream.userstream(encoding='utf8')
    except Exception, exc:
      if exc.args and 'timed out' in exc.args:
        pass
      else:
        print >> sys.stderr, exc 

if __name__ == "__main__":
    main()
