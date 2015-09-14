#!/usr/bin/env python

from __future__ import print_function

from time import sleep

import re
import StringIO
import json
import os
import random
import re
import string
import sys
import traceback
import tweepy

UNICODE_POO = u"\U0001F4A9"


def space_indices(text):
  return [i for i, x in enumerate(text) if x == u' ']


def mangle_status_fill(text, sender):
  # Make a poo in an empty space.
  chars = list(text)
  candidate_indices = space_indices(chars)
  idx = random.choice(candidate_indices)
  chars[idx] = UNICODE_POO
  result = u''.join(chars)
  return u'%s\n@%s' % (result, sender)


def print_offset(io, do_poo, src_line, x_offset):
  if do_poo:
    poo = UNICODE_POO
  else:
    poo = u''

  if x_offset < 0:
    fmt_tuple = (poo, u' ' * abs(x_offset), src_line)
  else:
    fmt_tuple = (src_line, u' ' * abs(x_offset), poo)

  if not (fmt_tuple[0] or fmt_tuple[2]):
    print(u'', file=io)
  elif not (fmt_tuple[2]):
    print(u'%s' % fmt_tuple[0], file=io)
  else:
    print(u'%s%s%s' % fmt_tuple, file=io)


def mangle_status_offset(text, sender):
  # Make a poo by creating horizontal and vertical space.
  io = StringIO.StringIO()
  src_lines = text.split(u'\n')
  x_offset = random.randint(-8, 8)
  y_offset = random.randint(-4, 4)
  curr_y = min(y_offset, 0)
  for src_line in src_lines:
    while curr_y < 0:
      print_offset(io, curr_y == y_offset, u'', x_offset)
      curr_y += 1
    print_offset(io, curr_y == y_offset, src_line, x_offset)
    curr_y += 1
  while curr_y <= y_offset:
    print_offset(io, curr_y == y_offset, u'', x_offset)
    curr_y += 1
  result = io.getvalue()
  io.close()
  return u'%s@%s' % (result, sender)


def log(line):
  print(line, file=sys.stderr)


class TinySpacePooListener(tweepy.StreamListener):
  def __init__(self, api):
    tweepy.StreamListener.__init__(self)
    self.api = api
    # self.status_mangler = StatusMangler()

  def on_status(self, status): #, tweet_id):
    # log(u"Received tweet author:'%s' text:'%s' id:%d" % (status.author.screen_name.lower(), status.text, status.id))
    # something in that log line keeps crashing with unicode.
    log(u'Received tweet.')

    # Only respond to specific account(s)
    # if status.author.screen_name.lower() in (u'tiny_star_field', u'mypalmike'):
    mangled_status = None
    if 'tiny_space_poo' not in status.text:  # Avoid bot looks by ignoring tweets mentioning me.
      if status.author.screen_name.lower() in (u'tiny_astro_naut', u'mypalmike'):
        log(u"Matched fill-space user")
        mangled_status = mangle_status_fill(status.text, status.author.screen_name)
      elif status.author.screen_name.lower() in (u'digital_henge'):
        log(u"Matched offset user")
        mangled_status = mangle_status_offset(status.text, status.author.screen_name)

      if mangled_status:
        # log(u"Status mangled:'%s'" % mangled_status)
        log(u"Mangled status.")
        self.api.update_status(status=mangled_status, in_reply_to_status_id=status.id)
      else:
        log(u"Skipped nonmatching user.")
    return True

  def on_exception(self, exc):
    traceback.print_exc(file=sys.stderr)
    return True

  def on_error(self, status_code):
    log('Encountered error with status code:', status_code)
    return True # Don't kill the stream

  def on_timeout(self):
    log('Timeout...')
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
  log("Starting")
  auth, api = get_auth_api()
  listener = TinySpacePooListener(api)
  stream = tweepy.Stream(auth, listener, timeout = 3600)

  log("Created stream. Calling userstream().")

  while True:
    try:
      stream.userstream(encoding='utf-8')
    except Exception as exc:
      if exc.args and 'timed out' in exc.args:
        pass
      else:
        traceback.print_exc(file=sys.stderr) 


if __name__ == "__main__":
  main()
