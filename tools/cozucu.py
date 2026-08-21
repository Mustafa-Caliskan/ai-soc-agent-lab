import sys

def reveal_hidden_text(text):
    """
    Emojinin arkasına gizlenmiş Unicode Tag karakterlerini tespit eder ve çözer.
    """
    # Sadece E0000 - E007F aralığındaki (gizli taglar) karakterleri ayıkla
    hidden = "".join([c for c in text if '\U000E0000' <= c <= '\U000E007F'])
    
    if not hidden:
        return None
        
    # Unicode Tag karakterlerini tekrar orijinal ASCII metne çevir (E0000 ofsetini çıkar)
    decoded = "".join([chr(ord(c) - 0xE0000) for c in hidden])
    return decoded

if __name__ == "__main__":
    print("\n" + "="*40)
    print("   CYBERTECH UNICODE DECODER (BLUE TEAM)")
    print("="*40)
    
    try:
        emoji_input = input("\n[?] Çözülecek emojiyi buraya yapıştırın: ").strip()
        
        result = reveal_hidden_text(emoji_input)
        
        print("\n" + "-"*40)
        print("ANALİZ SONUCU:")
        print("-"*40)
        
        if result:
            print(f"\n[!] TEHLİKE TESPİT EDİLDİ!")
            print(f"[!] Gizli Komut: {result}")
        else:
            print("\n[+] Temiz: Herhangi bir gizli metin bulunamadı.")
            
        print("\n" + "-"*40)
        
    except KeyboardInterrupt:
        print("\n\n[-] İşlem iptal edildi.")
