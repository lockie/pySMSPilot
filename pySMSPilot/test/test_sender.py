#!/usr/bin/env python
# -*- coding: utf-8 *-*
import unittest
from pySMSPilot import sender

# emulator api key, no real sending
API = u'XXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZXXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZ'
TEST_PHONE = u"79101234567"


class SmspilotTests(unittest.TestCase):
    def testNoApi(self):
        self.assertRaises(Exception, lambda _: sender.Sender(False))

    def testSender(self):
        client = sender.Sender(API)
        self.assertEqual(client.defaultSender, u"internet")
        client = sender.Sender(API, defaultSender=u"INFORM")
        self.assertEqual(client.defaultSender, u"INFORM")
        self.assertRaises(Exception, sender.Sender, API, defaultSender=u"1234556789012345667890")

    def test_build_data(self):
        client = sender.Sender(API)
        data = client.build_data(test="ok")
        self.assertEqual(API, data["apikey"])
        self.assertEqual("ok", data["test"])

        data = client.build_data({"test": "ok"})
        self.assertEqual(API, data["apikey"])
        self.assertEqual("ok", data["test"])

        data = client.build_data({"test": "ok"}, test2="ook")
        self.assertEqual(API, data["apikey"])
        self.assertEqual("ok", data["test"])
        self.assertEqual("ook", data["test2"])

    def testSingleSend(self):
        client = sender.Sender(API)
        client.defaultSender = "INFORM"
        client.addSMS(1, TEST_PHONE, u'Some text body')
        result = client.send()
        self.assertEqual(result[u'send'][0][u'text'], u'Some text body')
        self.assertEqual(result[u'send'][0][u'to'], TEST_PHONE)

    def testInvalidMessageId(self):
        client = sender.Sender(API)
        try:
            client.addSMS(1, TEST_PHONE, u'Some test text')
        except Exception as inst:
            self.assertEqual(str(inst), u'SMS with this id already queried')
        try:
            client.addSMS('invalid_str_id', TEST_PHONE, u'Some test text')
        except Exception as inst:
            self.assertEqual(str(inst), u'sms_id must be integer')

    def testInvalidSendTime(self):
        client = sender.Sender(API)
        try:
            client.addSMS(1, TEST_PHONE, u'Happy birthday!', None, '20.12.2013')
        except Exception as inst:
            self.assertEqual(str(inst), u'Invalid datetime! Must be GMT timestamp or YYYY-MM-DD HH:MM:SS')

    def testValidDateTimeSendTime(self):
        client = sender.Sender(API)
        import datetime
        send_date = datetime.datetime.now() + datetime.timedelta(hours=1)
        client.addSMS(1, TEST_PHONE, u'Happy birthday!', None, send_date)
        result = client.send()
        self.assertEqual(result[u'send'][0][u'text'], u'Happy birthday!')
        self.assertEqual(result[u'send'][0][u'to'], TEST_PHONE)
        self.assertEqual(send_date.strftime("%Y-%m-%d %H:%M:%S"), result[u'send'][0]['send_datetime'])

    def testTTL(self):
        client = sender.Sender(API)
        try:
            client.addSMS(1, TEST_PHONE, u'Happy birthday!', ttl=10)
            client.addSMS(2, TEST_PHONE, u'Happy birthday!', ttl=1440)
        except Exception as e:
            self.fail()

        self.assertRaises(Exception, client.addSMS, 3, TEST_PHONE, u'Happy birthday!', ttl=1441)
        self.assertRaises(Exception, client.addSMS, 4, TEST_PHONE, u'Happy birthday!', ttl=1)
        self.assertRaises(Exception, client.addSMS, 5, TEST_PHONE, u'Happy birthday!', ttl="Test")

    def test_callback_request(self):
        try:
            client = sender.Sender(API, callback="http://ya.ru/", callback_method="post")
        except Exception as e:
            self.fail("Valid callback method but %s" % str(e))
        client.addSMS(1, TEST_PHONE, u'Some test text')
        self.assertEqual(client.messages[0][u'callback'], "http://ya.ru/")
        self.assertEqual(client.messages[0][u'callback_method'], "post")
        try:
            client = sender.Sender(API, callback="http://ya.ru/", callback_method="get")
        except Exception as e:
            self.fail("Valid callback method but %s" % str(e))
        client.addSMS(1, TEST_PHONE, u'Some test text')
        self.assertEqual(client.messages[0][u'callback'], "http://ya.ru/")
        self.assertEqual(client.messages[0][u'callback_method'], "get")

    def test_balance(self):
        client = sender.Sender(API)
        result = client.checkBalance()
        self.assertIsInstance(result[u'balance'], float)

    def test_callback(self):
        # set method without url
        self.assertRaises(Exception, sender.Sender, API, callback_method="post")
        # set invalid url
        self.assertRaises(Exception, sender.Sender, API, callback="https://ya.ru/")
        # set invalid method
        self.assertRaises(Exception, sender.Sender, API, callback="http://ya.ru/", callback_method="put")

        try:
            client = sender.Sender(API, callback="http://ya.ru/")
        except Exception as e:
            self.fail("Valid callback but %s" % str(e))

    def testMultiSend(self):
        client = sender.Sender(API)
        client.addSMS(1, TEST_PHONE, u'Some test text')
        client.addSMS(2, TEST_PHONE[:-1]+"5", u'Some test text')
        result = client.send()
        self.assertEqual(result[u'send'][0][u'to'], TEST_PHONE)
        self.assertEqual(result[u'send'][1][u'to'], TEST_PHONE[:-1]+"5")
        self.assertEqual(result[u'send'][0][u'text'], u'Some test text')
        self.assertEqual(result[u'send'][1][u'text'], u'Some test text')


def main():
    unittest.main()

if __name__ == '__main__':
    main()
