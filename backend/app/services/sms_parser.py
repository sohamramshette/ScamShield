import re
import phonenumbers
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ParsedMessage:
    original_text: str
    normalized_text: str
    language: str
    urls: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    otps: List[str] = field(default_factory=list)
    wallets: List[str] = field(default_factory=list)
    upis: List[str] = field(default_factory=list)
    ips: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)


class SMSParser:
    URL_REGEX = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*')
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    UPI_REGEX = re.compile(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}')
    IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    OTP_REGEX = re.compile(r'\b\d{4,8}\b')
    # Basic BTC/ETH wallet detection
    WALLET_REGEX = re.compile(r'\b(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59}|0x[a-fA-F0-9]{40})\b')

    @classmethod
    def parse(cls, text: str) -> ParsedMessage:
        normalized = text.strip()
        
        parsed = ParsedMessage(
            original_text=text,
            normalized_text=normalized,
            language="en" # simplified for now
        )
        
        # Extract URLs
        parsed.urls = list(set(cls.URL_REGEX.findall(normalized)))
        
        # Extract Domains from URLs
        parsed.domains = []
        for url in parsed.urls:
            try:
                parsed.domains.append(urlparse(url).netloc.split(':')[0])
            except:
                pass
        parsed.domains = list(set(parsed.domains))
        
        # Extract Emails
        parsed.emails = list(set(cls.EMAIL_REGEX.findall(normalized)))
        
        # Extract UPI (filter out emails)
        potential_upis = list(set(cls.UPI_REGEX.findall(normalized)))
        parsed.upis = [upi for upi in potential_upis if upi not in parsed.emails]
        
        # Extract IPs
        parsed.ips = list(set(cls.IP_REGEX.findall(normalized)))
        
        # Extract Wallets
        parsed.wallets = list(set(cls.WALLET_REGEX.findall(normalized)))
        
        # Extract Phones using phonenumbers lib (finding matches in text)
        for match in phonenumbers.PhoneNumberMatcher(normalized, "US"): # Defaulting to US region for parsing, but handles + format well
            parsed.phones.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))
            
        parsed.phones = list(set(parsed.phones))
        
        # Detect OTPs (only if text contains OTP related keywords to avoid matching random numbers)
        if any(kw in normalized.lower() for kw in ['otp', 'code', 'verification', 'password', 'pin', 'verify']):
            parsed.otps = list(set(cls.OTP_REGEX.findall(normalized)))
            
        return parsed
