#!/usr/bin/python3

# tests assume you have a master server running on localhost:8080
import unittest
import requests as r
import random
import string

master = 'http://localhost:8080/'

# stolen from pynative.com
def randomString(stringLength=8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

class TestTKV(unittest.TestCase):
    def test_put(self):
        key1 = 'key1'
        val1 = 'val1'
        r.put(master + key1, val1)

        self.assertEqual(r.get(master + key1).text, val1)

    def test_delete(self):
        key2 = 'key2'
        val2 = 'val2'
        r.put(master + key2, val2)

        # make sure key got added
        self.assertEqual(r.get(master + key2).text, val2)

        r.delete(master + key2)

        # make sure key got deleted
        self.assertEqual(r.get(master + key2).status_code, 404)

    def test_10000_keys(self):
        key_vals = [(randomString(),randomString()) for i in range(100)]

        # add keys
        for key,val in key_vals:
            r.put(master + key, val)

        # assert that they're all there
        for key,val in key_vals:
            self.assertEqual(r.get(master + key).text, val)

        # delete them all
        for key,val in key_vals:
            r.delete(master + key)

        # assert they're all deleted
        for key,val in key_vals:
            self.assertEqual(r.get(master + key).status_code, 404)

    def test_no_overwrite(self):
        key3 = 'key3'
        val3 = 'val3'
        r.put(master + key3, val3)

        self.assertEqual(r.get(master + key3).text, val3)

        # try overwriting
        overwrite_req = r.put(master + key3, 'val4')

        # ensure that fails
        self.assertEqual(overwrite_req.status_code, 409)

        # assert val is still val3.
        self.assertEqual(r.get(master + key3).text, val3)



if __name__ == '__main__':
    unittest.main()

