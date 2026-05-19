import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, flash

app = Flask(_name_)
app.secret_key = "makyaj_v2_gizli_anahtar_9988"

# Genişletilmiş ve güvenli uzantı listesi
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return render_template('index.html', error="Lütfen bir fotoğraf seçin.")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error="Hiçbir dosya seçilmedi.")
            
        if file and allowed_file(file.filename):
            # --- RAM KORUMA AYARI BURAYA EKLENDİ ---
            # Fotoğrafı diske kaydetmeden direkt hafızada byte olarak okuyoruz
            file_bytes = np.fromstring(file.read(), np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if image is None:
                return render_template('index.html', error="Fotoğraf dosyası bozuk veya okunamadı. Başka bir resim deneyin.")
            
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Yüz bulunamazsa koruma
            if len(faces) == 0:
                return render_template('index.html', error="Fotoğrafta net bir yüz tespit edilemedi. Lütfen yüzünüzün net göründüğü bir fotoğraf yükleyin.")
            
            # --- SENİN ORİJİNAL PUANLAMA ALGORİTMAN (DOKUNULMADI) ---
            (x, y, w, h) = faces[0]
            base_calc = (w * h + x + y) % 50
            
            # Alt puanlar (4.0 ile 9.5 arası geniş aralık)
            goz_makyaji = round(4.0 + (base_calc % 5.5), 1)
            ten_uyumu = round(4.5 + (base_calc % 5.0), 1)
            ruj_dengesi = round(3.5 + (base_calc % 6.0), 1)
            far_uyumu = round(3.8 + (base_calc % 5.7), 1)
            
            # Genel ortalama skor
            toplam_skor = round((goz_makyaji + ten_uyumu + ruj_dengesi + far_uyumu) / 4, 1)
            if toplam_skor > 10.0: toplam_skor = 9.5
            if toplam_skor < 1.0: toplam_skor = 3.2

            # --- SENİN ORİJİNAL DOBLA JÜRİ YORUMLARIN (DOKUNULMADI) ---
            if toplam_skor >= 8.5:
                juri_notu = "Fena değil, makyajı gerçekten profesyonelce yapmışsın. Işıltın göz alıyor!"
            elif toplam_skor >= 7.0:
                juri_notu = "Günü kurtarır ama renk tercihleri biraz rüküş mü kalmış ne? Daha iyisini yapabilirsin."
            elif toplam_skor >= 5.5:
                juri_notu = "Yani... Aynaya bakmadan mı yaptın naptın? Parçalar uyuşmamış, aceleye gelmiş gibi."
            else:
                juri_notu = "Acele lavaboda bu kadar oluyor herhalde. Renkler birbirine girmiş, acilen silip baştan başlamalısın! Kötü olmuş."
            
            return render_template('result.html', 
                                   score=toplam_skor, 
                                   goz=goz_makyaji, 
                                   ten=ten_uyumu, 
                                   ruj=ruj_dengesi, 
                                   far=far_uyumu,
                                   yorum=juri_notu)
            
        else:
            return render_template('index.html', error="Geçersiz dosya formatı! Lütfen JPG, JPEG veya PNG yükleyin.")
            
    except Exception as e:
        print(f"KRİTİK HATA ENGELLENDİ: {e}")
        return render_template('index.html', error="Analiz sırasında teknik bir pürüz oluştu. Lütfen tekrar deneyin.")

if _name_ == '_main_':
    app.run(debug=True)
