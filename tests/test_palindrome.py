from unittest import TestCase
from app.models import is_palindrome


class WebserviceTestCase(TestCase): 

    def test_palindrome_empty_str(self):
        res = is_palindrome('')
        self.assertTrue(res)

    def test_palindrome_null(self):
        res =  is_palindrome(None)
        self.assertFalse(res)

    def test_palindrome_not_str(self):
        res =  is_palindrome({})
        self.assertFalse(res)

    def test_palindrome_is_palindrome_1(self):
        res =  is_palindrome('bb')
        self.assertTrue(res)

    def test_palindrome_is_palindrome_2(self):
        res =  is_palindrome('bb')
        self.assertTrue(res)

    def test_palindrome_is_palindrome_3(self):
        res =  is_palindrome('aba')
        self.assertTrue(res)

    def test_palindrome_is_palindrome_4(self):
        res =  is_palindrome('Bb')
        self.assertTrue(res)

    def test_palindrome_is_not_palindrome_1(self):
        res =  is_palindrome('bba')
        self.assertFalse(res)

    def test_palindrome_is_not_palindrome_2(self):
        res =  is_palindrome(' aba')
        self.assertFalse(res)

    def test_palindrome_is_not_palindrome_3(self):
        res =  is_palindrome('aba ')
        self.assertFalse(res)

    def test_palindrome_is_not_palindrome_4(self):
        res =  is_palindrome('()')
        self.assertFalse(res)

    def test_palindrome_is_not_palindrome_5(self):
        res =  is_palindrome('(aba)')
        self.assertFalse(res)        
