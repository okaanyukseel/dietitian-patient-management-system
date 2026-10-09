# Diyetisyen Hasta Takip Sistemi

Python (Tkinter) ve MySQL ile geliştirilmiş masaüstü uygulaması. Diyetisyenlerin hasta, hastalık, besin, diyet programı, ölçüm ve randevu kayıtlarını tek bir arayüzden yönetmesini sağlar.

## Özellikler

Uygulama, e-posta ve şifre ile giriş yapan diyetisyen için sekmeli bir panel açar:

| Sekme | İşlevler |
|---|---|
| Özet | Toplam hasta, besin çeşidi ve ileri tarihli randevu sayısı; tabloları `.sql` dosyasına `INSERT` komutları olarak yedekleme |
| Hastalar | Hasta ekleme, listeleme, güncelleme, silme |
| Hastalıklar | Hastalık tanımlama ve hastaya tanı atama |
| Besinler | Kalori / protein / karbonhidrat / yağ değerleriyle besin kütüphanesi (CRUD) |
| Diyet Yaz | Hastaya diyet programı oluşturma, gün ve öğüne göre besin ekleme, kalori analizi, listeyi PDF olarak dışa aktarma |
| Takip & Rapor | Su tüketimi ve kilo / bel / kalça ölçümü kaydı, hasta raporu ve günlük kalori ihtiyacı |
| Randevu | Randevu verme, güncelleme, iptal etme |
| Loglar | Yapılan işlemlerin son 50 kaydı |

Tüm SQL sorguları parametreli (`%s`) olarak çalıştırılır.

## Veritabanı

Uygulama `DiyetisyenDB` adlı bir MySQL veritabanı bekler. Kodda kullanılan nesneler:

- **Tablolar:** `Diyetisyenler`, `Hastalar`, `TanimliHastaliklar`, `HastaHastaliklari`, `Besinler`, `DiyetProgramlari`, `DiyetDetaylari`, `Olcumler`, `SuTakibi`, `Randevular`, `SistemLoglari`
- **Stored procedure'ler:** `Program_Analizi`, `Hasta_Raporu_Getir`
- **Fonksiyon:** `Kalori_Ihtiyaci_Hesapla`

> Veritabanı şema (DDL) dosyası bu repoda yer almamaktadır.

## Teknolojiler

- Python, Tkinter / ttk
- MySQL (`mysql-connector-python`)
- ReportLab (PDF çıktısı, opsiyonel; yüklü değilse PDF özelliği devre dışı kalır)

## Kurulum ve Çalıştırma

```bash
pip install -r requirements.txt
```

Bağlantı bilgileri ortam değişkenlerinden okunur:

| Değişken | Varsayılan |
|---|---|
| `DB_HOST` | `localhost` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | (boş) |
| `DB_NAME` | `DiyetisyenDB` |

```bash
# Windows (PowerShell)
$env:DB_PASSWORD="sifreniz"
python diyetisyenV5.py
```

## Proje Yapısı

```
diyetisyenV5.py      # Uygulamanın tamamı (giriş ekranı + yönetim paneli)
requirements.txt
```
