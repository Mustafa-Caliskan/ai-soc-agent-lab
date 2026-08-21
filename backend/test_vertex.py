import os
import vertexai
from vertexai.generative_models import GenerativeModel

# Ayarlar
PROJECT_ID = "gen-lang-client-0280788671"
LOCATION = "europe-west1"
KEY_FILE = "../frontend/gen-lang-client-0280788671-07eaaa562dfe.json"

def test_vertex():
    try:
        print(f"--- Vertex AI Test Başlatılıyor ---")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Test için 2.5-flash
        model = GenerativeModel("gemini-2.5-flash")
        
        print("Model çağrılıyor...")
        response = model.generate_content("Merhaba, çalışıyor musun?")
        print(f"BAŞARILI! Yanıt: {response.text}")
        
    except Exception as e:
        print(f"HATA ALINDI: {e}")

if __name__ == "__main__":
    test_vertex()
