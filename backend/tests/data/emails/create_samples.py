import os

samples = {
    "safe_email.eml": """Received: from mail.google.com (mail.google.com [142.250.114.108])
	by mx.scamshield.local (Postfix) with ESMTPS id 3A4B5C6D
	for <user@scamshield.ai>; Wed, 18 Jul 2026 10:20:30 +0000 (UTC)
Authentication-Results: mx.scamshield.local;
	dkim=pass header.i=@google.com header.s=20221208 header.b=XyZ123;
	spf=pass (google.com: domain of bob@google.com designates 142.250.114.108 as permitted sender) smtp.mailfrom=bob@google.com;
	dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=google.com
From: Bob Smith <bob@google.com>
To: user@scamshield.ai
Subject: Project update meeting
Message-ID: <12345.67890@google.com>
Date: Wed, 18 Jul 2026 10:20:00 +0000
Content-Type: text/plain; charset="utf-8"

Hi team,

Just a reminder that our project update meeting is scheduled for tomorrow at 10 AM.
Please review the attached notes beforehand.

Best,
Bob
""",
    "bank_phishing.eml": """Received: from unknown-server.ru (unknown.ru [192.168.1.100])
	by mx.scamshield.local (Postfix) with ESMTP id 9F8E7D6C
	for <victim@scamshield.ai>; Wed, 18 Jul 2026 11:20:30 +0000 (UTC)
Authentication-Results: mx.scamshield.local;
	dkim=fail header.i=@chase-alert.com header.s=badkey header.b=XyZ123;
	spf=fail (chase-alert.com: domain of support@chase-alert.com does not designate 192.168.1.100 as permitted sender) smtp.mailfrom=support@chase-alert.com;
	dmarc=fail (p=NONE sp=NONE dis=NONE) header.from=chase-alert.com
From: Chase Security <support@chase-alert.com>
To: victim@scamshield.ai
Subject: URGENT: Your account has been suspended
Message-ID: <bad.actor@chase-alert.com>
Date: Wed, 18 Jul 2026 11:20:00 +0000
Content-Type: text/html; charset="utf-8"

<html><body>
<h2>SECURITY ALERT</h2>
<p>Your Chase account has been temporarily suspended due to suspicious login attempts.</p>
<p>You must verify your identity immediately or your account will be permanently closed in 24 hours.</p>
<a href="http://www.chase-secure-verify-login-992.com/login">Click here to verify your account</a>
</body></html>
""",
    "fake_microsoft_login.eml": """Received: from compromised.host.com (compromised.com [10.0.0.5])
	by mx.scamshield.local (Postfix) with ESMTP id 11223344
	for <user@scamshield.ai>; Wed, 18 Jul 2026 12:20:30 +0000 (UTC)
Authentication-Results: mx.scamshield.local;
	dkim=none; spf=softfail; dmarc=none
From: Microsoft 365 Team <admin@it-support-portal-01.net>
To: user@scamshield.ai
Subject: Password Expiring in 2 Hours
Message-ID: <ms365@it-support-portal-01.net>
Date: Wed, 18 Jul 2026 12:20:00 +0000
Content-Type: text/html; charset="utf-8"

<html><body>
<p>Dear User,</p>
<p>Your Office 365 password is set to expire in 2 hours.</p>
<p>Please keep your current password by clicking the link below:</p>
<p><a href="http://login.microsoftonline.com.baddomain.net/update">Keep Password Same</a></p>
</body></html>
"""
}

# Write files
for name, content in samples.items():
    with open(f"C:/Users/lenovo/OneDrive/Desktop/ScamShield/backend/tests/data/emails/{name}", "w") as f:
        f.write(content)

print("Sample EML files created successfully.")
