import re

def is_ip_safe(ip):
    # Regex kullanarak metnin içinden SADECE IP kısmını çekiyoruz
    # Bu sayede IP'nin yanındaki parantez, tırnak veya nokta her şeyi eliyoruz
    match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip)
    
    if not match:
        return False
        
    clean_ip = match.group(0)
    
    # Yasaklı listesi
    blacklisted_ips = ["127.0.0.1", "0.0.0.0", "localhost"]
    
    if clean_ip in blacklisted_ips:
        return False
    
    # İç ağları koru (192.168.x.x, 10.x.x.x vb.)
    if clean_ip.startswith("192.168.") or clean_ip.startswith("10."):
        return False
        
    return True

def sanitize_input(text):
    # Saldırı anahtar kelimelerini daha kapsamlı yakala
    forbidden = [
        "ignore previous", 
        "talimatları unut", 
        "system override",
        "you are now",
        "admin access"
    ]
    for word in forbidden:
        if word in text.lower():
            return False
    return True