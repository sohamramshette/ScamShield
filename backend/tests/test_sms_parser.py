import pytest
from app.services.sms_parser import SMSParser

def test_sms_parser_extracts_urls():
    text = "Check this out: https://phishing.com/login and http://evil.com"
    parsed = SMSParser.parse(text)
    assert "https://phishing.com/login" in parsed.urls
    assert "http://evil.com" in parsed.urls
    assert "phishing.com" in parsed.domains
    assert "evil.com" in parsed.domains

def test_sms_parser_extracts_phones():
    text = "Call me at +1-800-555-1234 or +919876543210."
    parsed = SMSParser.parse(text)
    assert "+18005551234" in parsed.phones
    assert "+919876543210" in parsed.phones

def test_sms_parser_extracts_emails_and_upis():
    text = "Send money to scammer@ybl or email me at fake@support.com"
    parsed = SMSParser.parse(text)
    assert "fake@support.com" in parsed.emails
    assert "scammer@ybl" in parsed.upis
    # Ensure email is not mistakenly classified as UPI
    assert "fake@support.com" not in parsed.upis

def test_sms_parser_extracts_otp():
    text = "Your bank OTP code is 492105. Do not share."
    parsed = SMSParser.parse(text)
    assert "492105" in parsed.otps

def test_sms_parser_does_not_extract_random_numbers_as_otp():
    text = "I bought 492105 apples today."
    parsed = SMSParser.parse(text)
    assert len(parsed.otps) == 0

def test_sms_parser_extracts_wallets():
    text = "Send BTC to bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    parsed = SMSParser.parse(text)
    assert "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh" in parsed.wallets
