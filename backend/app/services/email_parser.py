import email
from email.policy import default
from email.parser import BytesParser
import re
import hashlib
from urllib.parse import urlparse
import io
from PIL import Image
try:
    from pyzbar.pyzbar import decode
except Exception:
    decode = None
import extract_msg

class ParsedAttachment:
    def __init__(self, filename, mime_type, size, sha256):
        self.filename = filename
        self.mime_type = mime_type
        self.size = size
        self.sha256 = sha256
        self.extension = filename.split(".")[-1].lower() if filename and "." in filename else ""

class ParsedHop:
    def __init__(self, hop_number, server_name, ip_address, timestamp):
        self.hop_number = hop_number
        self.server_name = server_name
        self.ip_address = ip_address
        self.timestamp = timestamp

class ParsedEmail:
    def __init__(self):
        self.subject = ""
        self.sender = ""
        self.reply_to = ""
        self.return_path = ""
        self.message_id = ""
        self.date = ""
        
        self.spf = "Unknown"
        self.dkim = "Unknown"
        self.dmarc = "Unknown"
        
        self.body_text = ""
        self.body_html = ""
        self.urls = set()
        self.attachments = []
        self.hops = []
        
        self.qr_code_urls = set()

class EmailParser:
    URL_REGEX = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*')
    IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

    @classmethod
    def parse_eml_bytes(cls, raw_bytes: bytes) -> ParsedEmail:
        msg = BytesParser(policy=default).parsebytes(raw_bytes)
        # Check if this is likely just plain text (no standard headers found)
        has_standard_headers = any(msg.get(h) for h in ["From", "To", "Subject", "Date", "Message-ID", "Received"])
        if not has_standard_headers:
            parsed = ParsedEmail()
            parsed.body_text = raw_bytes.decode('utf-8', errors='ignore')
            parsed.sender = "Pasted Text"
            parsed.subject = "Raw Text Analysis"
            cls._extract_urls_from_text(parsed)
            return parsed
            
        return cls._parse_email_message(msg)
        
    @classmethod
    def parse_eml_string(cls, raw_string: str) -> ParsedEmail:
        msg = email.message_from_string(raw_string, policy=default)
        # Check if this is likely just plain text (no standard headers found)
        has_standard_headers = any(msg.get(h) for h in ["From", "To", "Subject", "Date", "Message-ID", "Received"])
        if not has_standard_headers:
            parsed = ParsedEmail()
            parsed.body_text = raw_string
            parsed.sender = "Pasted Text"
            parsed.subject = "Raw Text Analysis"
            cls._extract_urls_from_text(parsed)
            return parsed
            
        return cls._parse_email_message(msg)

    @classmethod
    def parse_msg_bytes(cls, raw_bytes: bytes) -> ParsedEmail:
        # extract-msg takes a file path or file-like object
        msg_obj = extract_msg.Message(io.BytesIO(raw_bytes))
        parsed = ParsedEmail()
        parsed.subject = msg_obj.subject or ""
        parsed.sender = msg_obj.sender or ""
        parsed.date = str(msg_obj.date)
        parsed.message_id = msg_obj.messageId or ""
        
        parsed.body_text = msg_obj.body or ""
        parsed.body_html = msg_obj.htmlBody.decode('utf-8', errors='ignore') if msg_obj.htmlBody else ""
        
        cls._extract_urls_from_text(parsed)
        
        for att in msg_obj.attachments:
            data = att.data
            if data:
                sha = hashlib.sha256(data).hexdigest()
                parsed.attachments.append(ParsedAttachment(
                    filename=att.longFilename or att.shortFilename or "unknown",
                    mime_type="application/octet-stream", # MSG doesn't explicitly expose MIME well
                    size=len(data),
                    sha256=sha
                ))
                cls._scan_qr_in_image(data, parsed)
                
        # Try to get headers if present in MSG
        if msg_obj.header:
            # We can parse the MSG transport headers as an EML string
            header_str = msg_obj.header.as_string()
            eml_headers = email.message_from_string(header_str, policy=default)
            cls._extract_auth_headers(eml_headers, parsed)
            cls._extract_hops(eml_headers, parsed)
            
        return parsed

    @classmethod
    def _parse_email_message(cls, msg) -> ParsedEmail:
        parsed = ParsedEmail()
        parsed.subject = msg.get("Subject", "")
        parsed.sender = msg.get("From", "")
        parsed.reply_to = msg.get("Reply-To", "")
        parsed.return_path = msg.get("Return-Path", "")
        parsed.message_id = msg.get("Message-ID", "")
        parsed.date = msg.get("Date", "")
        
        cls._extract_auth_headers(msg, parsed)
        cls._extract_hops(msg, parsed)
        
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disp = str(part.get('Content-Disposition'))
            
            if "attachment" in content_disp or part.get_filename():
                cls._process_attachment(part, parsed)
            elif content_type == "text/plain":
                try:
                    parsed.body_text += part.get_content()
                except Exception:
                    pass
            elif content_type == "text/html":
                try:
                    parsed.body_html += part.get_content()
                except Exception:
                    pass
            elif "image" in content_type:
                # Embedded images
                cls._process_attachment(part, parsed)

        cls._extract_urls_from_text(parsed)
        return parsed

    @classmethod
    def _extract_auth_headers(cls, msg, parsed: ParsedEmail):
        auth_results = str(msg.get_all("Authentication-Results", ""))
        
        if "spf=pass" in auth_results.lower(): parsed.spf = "Pass"
        elif "spf=softfail" in auth_results.lower(): parsed.spf = "Soft Fail"
        elif "spf=fail" in auth_results.lower(): parsed.spf = "Fail"
        
        if "dkim=pass" in auth_results.lower(): parsed.dkim = "Pass"
        elif "dkim=fail" in auth_results.lower(): parsed.dkim = "Fail"
        
        if "dmarc=pass" in auth_results.lower(): parsed.dmarc = "Pass"
        elif "dmarc=fail" in auth_results.lower(): parsed.dmarc = "Fail"

    @classmethod
    def _extract_hops(cls, msg, parsed: ParsedEmail):
        received_headers = msg.get_all("Received")
        if not received_headers:
            return
            
        # Received headers are appended to the front by MTAs, so we reverse to get timeline
        received_headers.reverse()
        for idx, rec in enumerate(received_headers):
            # Extract basic server and IP
            server = "Unknown"
            ip = "Unknown"
            ts = "Unknown"
            
            if "from" in rec.lower():
                parts = rec.split("\n")
                first_line = parts[0]
                ip_match = cls.IP_REGEX.search(first_line)
                if ip_match: ip = ip_match.group()
                
            if ";" in rec:
                ts = rec.split(";")[-1].strip()
                
            parsed.hops.append(ParsedHop(
                hop_number=idx+1,
                server_name=server,
                ip_address=ip,
                timestamp=ts
            ))

    @classmethod
    def _process_attachment(cls, part, parsed: ParsedEmail):
        filename = part.get_filename() or "embedded_object"
        data = part.get_payload(decode=True)
        if not data: return
        
        sha = hashlib.sha256(data).hexdigest()
        parsed.attachments.append(ParsedAttachment(
            filename=filename,
            mime_type=part.get_content_type(),
            size=len(data),
            sha256=sha
        ))
        
        if "image" in part.get_content_type():
            cls._scan_qr_in_image(data, parsed)

    @classmethod
    def _extract_urls_from_text(cls, parsed: ParsedEmail):
        urls = cls.URL_REGEX.findall(parsed.body_text)
        urls += cls.URL_REGEX.findall(parsed.body_html)
        
        for url in urls:
            # clean url
            url = url.strip('\'"<>')
            parsed.urls.add(url)

    @classmethod
    def _scan_qr_in_image(cls, data: bytes, parsed: ParsedEmail):
        if not decode:
            return
        try:
            img = Image.open(io.BytesIO(data))
            result = decode(img)
            for r in result:
                url = r.data.decode('utf-8')
                if url.startswith("http"):
                    parsed.qr_code_urls.add(url)
                    parsed.urls.add(url)
        except Exception:
            pass
