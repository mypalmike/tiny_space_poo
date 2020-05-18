#!/usr/bin/env python

from time import sleep

import re
from io import StringIO
import json
import logging
import os
import random
import re
import string
import sys
import traceback
import tweepy

UNICODE_POO = '\U0001F4A9'

ID_MYPALMIKE = '233950108'
ID_TINY_ASTRO_NAUT = '2758649640'
ID_DIGITAL_HENGE = '3062148770'
ID_ASCIIGALAXY = '980223140574806017'

def space_indices(text):
  # Spaces or the wide dot used by asciigalaxy
  return [i for i, x in enumerate(text) if x in (' ', '．')]


def mangle_status_fill(text, sender):
  # Make a poo in an empty space.
  chars = list(text)
  candidate_indices = space_indices(chars)
  idx = random.choice(candidate_indices)
  chars[idx] = UNICODE_POO
  result = ''.join(chars)
  return '%s\n@%s' % (result, sender)


def print_offset(io, do_poo, src_line, x_offset):
  if do_poo:
    poo = UNICODE_POO
  else:
    poo = ''

  if x_offset < 0:
    fmt_tuple = (poo, ' ' * abs(x_offset), src_line)
  else:
    fmt_tuple = (src_line, ' ' * abs(x_offset), poo)

  if not (fmt_tuple[0] or fmt_tuple[2]):
    print('', file=io)
  elif not (fmt_tuple[2]):
    print('%s' % fmt_tuple[0], file=io)
  else:
    print('%s%s%s' % fmt_tuple, file=io)


def mangle_status_offset(text, sender):
  # Make a poo by creating horizontal and vertical space.
  io = StringIO()
  src_lines = text.split('\n')
  x_offset = random.randint(-8, 8)
  y_offset = random.randint(-4, 4)
  curr_y = min(y_offset, 0)
  for src_line in src_lines:
    while curr_y < 0:
      print_offset(io, curr_y == y_offset, '', x_offset)
      curr_y += 1
    print_offset(io, curr_y == y_offset, src_line, x_offset)
    curr_y += 1
  while curr_y <= y_offset:
    print_offset(io, curr_y == y_offset, '', x_offset)
    curr_y += 1
  result = io.getvalue()
  io.close()
  return '%s@%s' % (result, sender)


class TinySpacePooListener(tweepy.StreamListener):
  def __init__(self, api):
    tweepy.StreamListener.__init__(self)
    self.api = api

  def on_status(self, status): #, tweet_id):
    logging.info('Received tweet from {} text is {}.'.format(status.author.screen_name, status.text))

    mangled_status = None
    if 'tiny_space_poo' not in status.text:  # Avoid bot loops by ignoring tweets mentioning me.
      if status.author.screen_name.lower() in ('tiny_astro_naut', 'asciigalaxy'): # , 'mypalmike'):
        logging.info('Matched fill-space user')
        mangled_status = mangle_status_fill(status.text, status.author.screen_name)
      elif status.author.screen_name.lower() in ('digital_henge'):
        logging.info('Matched offset user')
        mangled_status = mangle_status_offset(status.text, status.author.screen_name)

      if mangled_status:
        # logging.info('Status mangled:'%s'' % mangled_status)
        logging.info('Mangled status.')
        self.api.update_status(status=mangled_status, in_reply_to_status_id=status.id)
      else:
        logging.info('Skipped nonmatching user.')
    return True

  def on_exception(self, exc):
    traceback.print_exc(file=sys.stderr)
    return True

  def on_error(self, status_code):
    logging.error('Encountered error with status code: {}'.format(status_code))
    if status_code == 420:
      return False
    return True # Don't kill the stream

  def on_timeout(self):
    logging.error('Timeout...')
    return True # Don't kill the stream


def get_creds():
  with open('creds', 'r') as f:
    return [line.strip() for line in f]


def get_auth_api():
  k, s1, t, s2 = get_creds()
  auth = tweepy.OAuthHandler(k, s1)
  auth.set_access_token(t, s2)
  return [auth, tweepy.API(auth)]


def main(argv = sys.argv):
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

  logging.warn('Starting')

  auth, api = get_auth_api()
  listener = TinySpacePooListener(api)
  stream = tweepy.Stream(auth, listener, timeout = 3600)

  logging.info('Created stream. Calling stream.filter()...')

  while True:
    try:
      stream.filter(follow=[ID_MYPALMIKE, ID_TINY_ASTRO_NAUT, ID_DIGITAL_HENGE, ID_ASCIIGALAXY])
    except Exception as exc:
      if exc.args and 'timed out' in exc.args:
        pass
      else:
        traceback.print_exc(file=sys.stderr) 


if __name__ == '__main__':
  main()
  
