"""
Phishing URL Detector
Loads the trained Random Forest model (phishing_rf_model.pkl) and extracts
URL-based features for phishing detection in chat messages.
"""

import re
import os
import pickle
import math
import warnings
import numpy as np
import pandas as pd
from urllib.parse import urlparse

# ─────────────────────────────────────────────
# Feature column order MUST match training data
# (after dropping FILENAME, URL, Domain, TLD, Title)
# ─────────────────────────────────────────────
FEATURE_COLUMNS = [
    'URLLength', 'DomainLength', 'IsDomainIP', 'URLSimilarityIndex',
    'CharContinuationRate', 'TLDLegitimateProb', 'URLCharProb', 'TLDLength',
    'NoOfSubDomain', 'HasObfuscation', 'NoOfObfuscatedChar', 'ObfuscationRatio',
    'NoOfLettersInURL', 'LetterRatioInURL', 'NoOfDegitsInURL', 'DegitRatioInURL',
    'NoOfEqualsInURL', 'NoOfQMarkInURL', 'NoOfAmpersandInURL',
    'NoOfOtherSpecialCharsInURL', 'SpacialCharRatioInURL', 'IsHTTPS',
    'LineOfCode', 'LargestLineLength', 'HasTitle', 'DomainTitleMatchScore',
    'URLTitleMatchScore', 'HasFavicon', 'Robots', 'IsResponsive',
    'NoOfURLRedirect', 'NoOfSelfRedirect', 'HasDescription', 'NoOfPopup',
    'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton',
    'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto',
    'HasCopyrightInfo', 'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef',
    'NoOfEmptyRef', 'NoOfExternalRef'
]

# TLD legitimacy scores (based on commonality of legitimate sites)
TLD_LEGIT_PROB = {
    'com': 0.523, 'org': 0.200, 'net': 0.190, 'edu': 0.950, 'gov': 0.990,
    'uk': 0.029, 'de': 0.033, 'fr': 0.028, 'au': 0.031, 'ca': 0.035,
    'jp': 0.040, 'cn': 0.015, 'ru': 0.010, 'in': 0.025, 'br': 0.022,
    'io': 0.060, 'co': 0.040, 'info': 0.050, 'biz': 0.030, 'us': 0.045,
    'nl': 0.032, 'it': 0.028, 'es': 0.027, 'pl': 0.020, 'se': 0.021,
    'xyz': 0.005, 'tk': 0.002, 'top': 0.003, 'club': 0.004, 'online': 0.006,
    'site': 0.005, 'website': 0.004, 'live': 0.006, 'space': 0.003,
}

# URL keywords for feature extraction
BANK_KEYWORDS = ['bank', 'banking', 'account', 'secure', 'signin', 'login', 'verify', 'wallet']
PAY_KEYWORDS = ['pay', 'payment', 'paypal', 'paytm', 'venmo', 'cashapp', 'zelle', 'stripe', 'checkout']
CRYPTO_KEYWORDS = ['crypto', 'bitcoin', 'btc', 'eth', 'ethereum', 'blockchain', 'wallet', 'coin', 'token', 'nft']


def _is_ip_address(hostname: str) -> bool:
    """Check if a hostname is an IP address."""
    ip_pattern = r'^\d{1,3}(\.\d{1,3}){3}$'
    return bool(re.match(ip_pattern, hostname))


def _get_tld(hostname: str) -> str:
    """Extract TLD from hostname."""
    parts = hostname.split('.')
    return parts[-1].lower() if parts else ''


def _char_continuation_rate(url: str) -> float:
    """Ratio of consecutive same-character pairs to total chars."""
    if len(url) <= 1:
        return 0.0
    consecutive = sum(1 for i in range(len(url) - 1) if url[i] == url[i + 1])
    return consecutive / (len(url) - 1)


def _url_char_prob(url: str) -> float:
    """Estimate character probability (entropy-based, lower = more random = more suspicious)."""
    if not url:
        return 0.0
    freq = {}
    for c in url:
        freq[c] = freq.get(c, 0) + 1
    entropy = -sum((v / len(url)) * math.log2(v / len(url)) for v in freq.values())
    # Normalize: typical URLs have entropy ~3.5-4.5
    return max(0.0, min(1.0, 1.0 - (entropy / 6.0)))


def _count_obfuscated(url: str) -> int:
    """Count percent-encoded characters in URL."""
    return len(re.findall(r'%[0-9a-fA-F]{2}', url))


def _count_other_special(url: str) -> int:
    """Count special chars that aren't typical URL chars."""
    typical = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&\'()*+,;=%')
    return sum(1 for c in url if c not in typical)


def extract_url_features(url: str) -> dict:
    """
    Extract the 50 numeric features used during model training.
    Page-level features (HTML content) are set to 0 since we scan URLs at chat time.
    """
    try:
        parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'http://' + url)
    except Exception:
        parsed = urlparse('http://unknown.com')

    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    full_url = url

    url_len = len(full_url)
    domain_len = len(hostname)
    is_ip = int(_is_ip_address(hostname))
    tld = _get_tld(hostname)
    tld_len = len(tld)

    # Subdomains: count dots minus 1 (www.example.com → 1 subdomain)
    parts = hostname.split('.')
    no_of_subdomain = max(0, len(parts) - 2)

    # Character stats
    letters = sum(1 for c in full_url if c.isalpha())
    digits = sum(1 for c in full_url if c.isdigit())
    letter_ratio = letters / url_len if url_len > 0 else 0
    digit_ratio = digits / url_len if url_len > 0 else 0

    n_equals = full_url.count('=')
    n_qmark = full_url.count('?')
    n_ampersand = full_url.count('&')
    n_other_special = _count_other_special(full_url)
    special_ratio = (n_equals + n_qmark + n_ampersand + n_other_special) / url_len if url_len > 0 else 0

    # Obfuscation
    n_obfuscated = _count_obfuscated(full_url)
    obfuscation_ratio = n_obfuscated / url_len if url_len > 0 else 0
    has_obfuscation = int(n_obfuscated > 0)

    # Entropy / character probability
    char_cont_rate = _char_continuation_rate(full_url)
    url_char_prob = _url_char_prob(full_url)

    # TLD legitimacy
    tld_legit_prob = TLD_LEGIT_PROB.get(tld.lower(), 0.010)

    # HTTPS
    is_https = int(parsed.scheme == 'https')

    # URL similarity index (use 100.0 for well-formed URLs, lower for suspicious)
    url_similarity_index = 50.0 if is_ip or has_obfuscation else 100.0

    # Keyword features (from URL string only)
    url_lower = full_url.lower()
    bank = int(any(k in url_lower for k in BANK_KEYWORDS))
    pay = int(any(k in url_lower for k in PAY_KEYWORDS))
    crypto = int(any(k in url_lower for k in CRYPTO_KEYWORDS))

    # Page-level features: we can't fetch the page at chat time, so use
    # realistic median values from the training dataset (observed from sample rows).
    # This keeps the model's decision driven by URL-level features rather than
    # treating every URL as a blank page (which caused false positives).
    page_features = {
        'LineOfCode': 300, 'LargestLineLength': 150, 'HasTitle': 1,
        'DomainTitleMatchScore': 60.0, 'URLTitleMatchScore': 50.0,
        'HasFavicon': 1, 'Robots': 1, 'IsResponsive': 1,
        'NoOfURLRedirect': 0, 'NoOfSelfRedirect': 0, 'HasDescription': 1,
        'NoOfPopup': 0, 'NoOfiFrame': 0, 'HasExternalFormSubmit': 0,
        'HasSocialNet': 0, 'HasSubmitButton': 0, 'HasHiddenFields': 0,
        'HasPasswordField': 0, 'HasCopyrightInfo': 1,
        'NoOfImage': 25, 'NoOfCSS': 10, 'NoOfJS': 12,
        'NoOfSelfRef': 40, 'NoOfEmptyRef': 1, 'NoOfExternalRef': 60,
    }

    features = {
        'URLLength': url_len,
        'DomainLength': domain_len,
        'IsDomainIP': is_ip,
        'URLSimilarityIndex': url_similarity_index,
        'CharContinuationRate': char_cont_rate,
        'TLDLegitimateProb': tld_legit_prob,
        'URLCharProb': url_char_prob,
        'TLDLength': tld_len,
        'NoOfSubDomain': no_of_subdomain,
        'HasObfuscation': has_obfuscation,
        'NoOfObfuscatedChar': n_obfuscated,
        'ObfuscationRatio': obfuscation_ratio,
        'NoOfLettersInURL': letters,
        'LetterRatioInURL': letter_ratio,
        'NoOfDegitsInURL': digits,
        'DegitRatioInURL': digit_ratio,
        'NoOfEqualsInURL': n_equals,
        'NoOfQMarkInURL': n_qmark,
        'NoOfAmpersandInURL': n_ampersand,
        'NoOfOtherSpecialCharsInURL': n_other_special,
        'SpacialCharRatioInURL': special_ratio,
        'IsHTTPS': is_https,
        'Bank': bank,
        'Pay': pay,
        'Crypto': crypto,
        **page_features,
    }

    return features


def features_to_array(features: dict) -> pd.DataFrame:
    """Convert features dict to a single-row DataFrame in the correct column order."""
    row = {col: features.get(col, 0) for col in FEATURE_COLUMNS}
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


# ─────────────────────────────────────────────
# Model loader (singleton)
# ─────────────────────────────────────────────
_phishing_model = None

def load_phishing_model(model_path: str = 'phishing_rf_model.pkl') -> bool:
    """Load the trained phishing Random Forest model. Returns True on success."""
    global _phishing_model
    try:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_path)
        with open(full_path, 'rb') as f:
            _phishing_model = pickle.load(f)
        print(f"✅ Phishing model loaded successfully from {model_path}")
        return True
    except FileNotFoundError:
        print(f"❌ Phishing model file not found: {model_path}")
        return False
    except Exception as e:
        print(f"❌ Failed to load phishing model: {e}")
        return False


# ─────────────────────────────────────────────
# URL extraction from text
# ─────────────────────────────────────────────
URL_REGEX = re.compile(
    r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
    r'(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+'
    r'(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»""'']))'
)


def extract_urls(text: str) -> list:
    """Extract all URLs from a text string."""
    return URL_REGEX.findall(text)


# ─────────────────────────────────────────────
# Main prediction function
# ─────────────────────────────────────────────
def _is_whitelisted(url: str) -> bool:
    """Return True for localhost / private IPs that should never be flagged."""
    try:
        parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'http://' + url)
        host = (parsed.hostname or '').lower()
    except Exception:
        return False
    # Exact matches
    if host in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
        return True
    # Private IP ranges: 10.x, 172.16-31.x, 192.168.x
    import re as _re
    if _re.match(r'^10\.', host): return True
    if _re.match(r'^172\.(1[6-9]|2\d|3[01])\.', host): return True
    if _re.match(r'^192\.168\.', host): return True
    if _re.match(r'^127\.', host): return True
    return False


def check_urls_in_message(message: str) -> list:
    """
    Scan a chat message for URLs and check each one for phishing.

    Returns a list of dicts, one per URL found:
    {
        'url': str,
        'is_phishing': bool,   # True if label == 0 (phishing)
        'confidence': float,   # 0.0–1.0
        'label': int           # 0 = phishing, 1 = legitimate
    }
    If model is not loaded, returns an empty list.
    """
    if _phishing_model is None:
        return []

    urls = extract_urls(message)
    results = []

    for url in urls:
        try:
            # Skip localhost / private IP — always safe
            if _is_whitelisted(url):
                results.append({
                    'url': url,
                    'is_phishing': False,
                    'confidence': 0.0,
                    'label': 1,
                })
                continue

            features = extract_url_features(url)
            arr = features_to_array(features)

            # model labels: 0 = phishing, 1 = legitimate
            proba = _phishing_model.predict_proba(arr)[0]   # [P(phishing), P(legit)]
            label = int(_phishing_model.predict(arr)[0])
            phishing_prob = float(proba[0])                  # probability of class 0

            results.append({
                'url': url,
                'is_phishing': label == 0,
                'confidence': round(phishing_prob * 100, 1),  # as percentage
                'label': label,
            })
        except Exception as e:
            # Don't crash the chat on a bad URL
            results.append({
                'url': url,
                'is_phishing': False,
                'confidence': 0.0,
                'label': 1,
                'error': str(e),
            })

    return results
