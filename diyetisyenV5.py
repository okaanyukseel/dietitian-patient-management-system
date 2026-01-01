import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import os

# PDF Kütüphanesi Kontrolü
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AKTIF = True
except ImportError:
    PDF_AKTIF = False

# =============================================================================
#  1. AYARLAR & VERİTABANI BAĞLANTISI
# =============================================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '0206',  # <-- BURAYA KENDİ MYSQL ŞİFRENİ YAZ
    'database': 'DiyetisyenDB'
}

# --- Renk Paleti ---
RENK_BG = "#F4F6F9"       
RENK_MENU = "#2C3E50"     
RENK_ACCENT = "#3498DB"   
RENK_BTN_SUCCESS = "#27AE60" 
RENK_BTN_DANGER = "#C0392B"  
RENK_BTN_WARNING = "#F39C12" 
RENK_TEXT = "#34495E"     
FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")

def baglan():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        messagebox.showerror("Bağlantı Hatası", f"Veritabanına bağlanılamadı:\n{e}")
        return None

aktif_diyetisyen_id = None
root = None

def log_tut(islem_tipi, aciklama):
    """SistemLoglari tablosuna kayıt atar"""
    if not aktif_diyetisyen_id: return
    try:
        conn = baglan(); cursor = conn.cursor()
        sql = "INSERT INTO SistemLoglari (DiyetisyenID, Tarih, IslemTipi, Aciklama) VALUES (%s, NOW(), %s, %s)"
        cursor.execute(sql, (aktif_diyetisyen_id, islem_tipi, aciklama))
        conn.commit(); conn.close()
    except: pass

def tr_duzelt(text):
    if not text: return ""
    cevir = str.maketrans("ğĞıİşŞçÇöÖüÜ", "gGiIsScCoOuU")
    return str(text).translate(cevir)

# =============================================================================
#  2. GİRİŞ EKRANI
# =============================================================================
def giris_ekrani():
    login_win = Tk()
    login_win.title("Giriş - Diyetisyen Sistemi")
    login_win.geometry("400x520")
    login_win.configure(bg=RENK_MENU)
    login_win.eval('tk::PlaceWindow . center')

    def giris_yap():
        global aktif_diyetisyen_id
        email = ent_email.get()
        sifre = ent_sifre.get()
        
        conn = baglan()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DiyetisyenID, Ad, Soyad FROM Diyetisyenler WHERE Email=%s AND Sifre=%s", (email, sifre))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                aktif_diyetisyen_id = user[0]
                log_tut("LOGIN", "Sisteme giriş yapıldı.")
                login_win.destroy()
                ana_uygulama(f"{user[1]} {user[2]}")
            else:
                messagebox.showerror("Hata", "Hatalı E-posta veya Şifre!")

    Label(login_win, text="🥑", bg=RENK_MENU, fg="white", font=("Segoe UI", 60)).pack(pady=(50, 10))
    Label(login_win, text="SAĞLIKLI YAŞAM\nMERKEZİ", bg=RENK_MENU, fg="white", font=("Segoe UI", 16, "bold")).pack(pady=10)
    
    frm = Frame(login_win, bg="white", padx=20, pady=30)
    frm.pack(fill="both", expand=True, padx=30, pady=30)
    
    Label(frm, text="E-Posta:", bg="white", fg=RENK_TEXT, font=FONT_BOLD).pack(anchor="w")
    ent_email = Entry(frm, font=FONT_NORMAL, bg="#ECF0F1", relief="flat"); ent_email.pack(fill="x", pady=(5, 15), ipady=5)
    
    Label(frm, text="Şifre:", bg="white", fg=RENK_TEXT, font=FONT_BOLD).pack(anchor="w")
    ent_sifre = Entry(frm, font=FONT_NORMAL, bg="#ECF0F1", relief="flat", show="●"); ent_sifre.pack(fill="x", pady=(5, 20), ipady=5)
    
    Button(frm, text="GİRİŞ YAP", command=giris_yap, bg=RENK_ACCENT, fg="white", font=FONT_BOLD, relief="flat", cursor="hand2").pack(fill="x", ipady=10)
    
    login_win.mainloop()

# =============================================================================
#  3. ANA UYGULAMA
# =============================================================================
def ana_uygulama(diyetisyen_adi):
    global root
    root = Tk()
    root.title(f"Diyetisyen Yönetim Paneli | Aktif Uzman: {diyetisyen_adi}")
    root.state('zoomed')
    root.configure(bg=RENK_BG)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TNotebook", background=RENK_BG, tabposition='n')
    style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 8], background="#BDC3C7", foreground=RENK_TEXT)
    style.map("TNotebook.Tab", background=[("selected", RENK_MENU)], foreground=[("selected", "white")])
    style.configure("Treeview", font=FONT_NORMAL, rowheight=28, background="white", fieldbackground="white")
    style.configure("Treeview.Heading", font=FONT_BOLD, background=RENK_MENU, foreground="white", relief="flat")
    style.configure("TLabelframe", background=RENK_BG, borderwidth=2, relief="groove")
    style.configure("TLabelframe.Label", background=RENK_BG, foreground=RENK_MENU, font=FONT_BOLD)

    header = Frame(root, bg=RENK_MENU, height=60)
    header.pack(fill="x")
    Label(header, text="Diyetisyen Hasta Takip Sistemi", bg=RENK_MENU, fg="white", font=("Segoe UI", 14, "bold")).pack(side="left", padx=20, pady=15)
    Label(header, text=f"Hoşgeldiniz, {diyetisyen_adi}", bg=RENK_MENU, fg="#BDC3C7", font=("Segoe UI", 10)).pack(side="right", padx=20, pady=15)

    tabs = ttk.Notebook(root)
    tabs.pack(expand=1, fill="both", padx=10, pady=10)

    t_home = Frame(tabs, bg=RENK_BG); tabs.add(t_home, text="🏠 ÖZET")
    t_hasta = Frame(tabs, bg=RENK_BG); tabs.add(t_hasta, text="👤 HASTALAR")
    t_saglik = Frame(tabs, bg=RENK_BG); tabs.add(t_saglik, text="💊 HASTALIKLAR")
    t_besin = Frame(tabs, bg=RENK_BG); tabs.add(t_besin, text="🍎 BESİNLER")
    t_diyet = Frame(tabs, bg=RENK_BG); tabs.add(t_diyet, text="📋 DİYET YAZ")
    t_takip = Frame(tabs, bg=RENK_BG); tabs.add(t_takip, text="⚖️ TAKİP & RAPOR")
    t_randevu = Frame(tabs, bg=RENK_BG); tabs.add(t_randevu, text="📅 RANDEVU")
    t_log = Frame(tabs, bg=RENK_BG); tabs.add(t_log, text="📜 LOGLAR")

    # --- TAB 0: DASHBOARD & YEDEKLEME ---
    def istatistikleri_guncelle():
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Hastalar")
        lbl_h.config(text=str(cursor.fetchone()[0]))
        cursor.execute("SELECT COUNT(*) FROM Besinler")
        lbl_b.config(text=str(cursor.fetchone()[0]))
        cursor.execute("SELECT COUNT(*) FROM Randevular WHERE TarihSaat >= NOW()")
        lbl_r.config(text=str(cursor.fetchone()[0]))
        conn.close()

    def sistem_yedegi_al():
        try:
            dosya_adi = f"Yedek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            conn = baglan(); cursor = conn.cursor()
            tablolar = ["Hastalar", "Besinler", "DiyetProgramlari", "DiyetDetaylari", "Olcumler", "SuTakibi", "Randevular", "HastaHastaliklari", "SistemLoglari"]
            
            with open(dosya_adi, "w", encoding="utf-8") as f:
                f.write(f"-- DiyetisyenDB Yedek: {datetime.now()}\n\n")
                for tablo in tablolar:
                    cursor.execute(f"SELECT * FROM {tablo}")
                    veriler = cursor.fetchall()
                    for veri in veriler:
                        veri_str = str(veri).replace("None", "NULL").replace("datetime.date", "").replace("datetime.datetime", "")
                        f.write(f"INSERT INTO {tablo} VALUES {veri_str};\n")
                    f.write("\n")
            
            messagebox.showinfo("Yedekleme Başarılı", f"Dosya kaydedildi:\n{os.path.abspath(dosya_adi)}")
            log_tut("YEDEKLEME", f"Veritabanı yedeği alındı: {dosya_adi}")
            conn.close()
        except Exception as e: messagebox.showerror("Hata", f"Yedek alınamadı: {e}")

    def kart_yap(parent, baslik, renk):
        f = Frame(parent, bg="white", bd=1, relief="solid")
        f.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        Frame(f, bg=renk, height=4).pack(fill="x")
        Label(f, text=baslik, bg="white", fg="#7F8C8D", font=("Segoe UI", 11)).pack(pady=(15, 5))
        lbl = Label(f, text="0", bg="white", fg=RENK_TEXT, font=("Segoe UI", 30, "bold"))
        lbl.pack(pady=(0, 15))
        return lbl

    fr_cards = Frame(t_home, bg=RENK_BG); fr_cards.pack(fill="x", padx=10, pady=20)
    lbl_h = kart_yap(fr_cards, "Toplam Hasta", RENK_ACCENT)
    lbl_b = kart_yap(fr_cards, "Besin Çeşidi", RENK_BTN_WARNING)
    lbl_r = kart_yap(fr_cards, "Aktif Randevular", RENK_BTN_SUCCESS)
    
    fr_btn = Frame(t_home, bg=RENK_BG); fr_btn.pack(pady=20)
    Button(fr_btn, text="🔄 Verileri Güncelle", command=istatistikleri_guncelle, bg=RENK_MENU, fg="white", height=2).pack(side="left", padx=10)
    Button(fr_btn, text="💾 SİSTEM YEDEĞİ AL", command=sistem_yedegi_al, bg="#8E44AD", fg="white", height=2).pack(side="left", padx=10)

    # --- TAB 1: HASTA İŞLEMLERİ ---
    def hasta_kaydet():
        conn = baglan()
        if conn:
            cursor = conn.cursor()
            sql = """INSERT INTO Hastalar (DiyetisyenID, Ad, Soyad, TCNo, Telefon, DogumTarihi, Cinsiyet, Boy, HedefKilo) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (aktif_diyetisyen_id, en_h_ad.get(), en_h_soy.get(), en_h_tc.get(), en_h_tel.get(), en_h_dt.get(), cb_h_cin.get(), en_h_boy.get(), en_h_hedef.get())
            try:
                cursor.execute(sql, val)
                conn.commit()
                log_tut("HASTA EKLE", f"{en_h_ad.get()} {en_h_soy.get()} eklendi.")
                messagebox.showinfo("Başarılı", "Hasta kaydedildi!")
                hasta_listele(); istatistikleri_guncelle(); combobox_guncelle()
                for e in [en_h_ad, en_h_soy, en_h_tc, en_h_tel, en_h_boy, en_h_hedef]: e.delete(0, END)
                en_h_dt.delete(0, END); en_h_dt.insert(0, "1990-01-01"); cb_h_cin.set('')
            except Exception as e: messagebox.showerror("Hata", str(e))
            conn.close()

    def hasta_sil():
        secili = tr_hasta.selection()
        if not secili: messagebox.showwarning("Uyarı", "Silinecek hastayı seçiniz"); return
        id = tr_hasta.item(secili)['values'][0]
        ad = tr_hasta.item(secili)['values'][1]
        if messagebox.askyesno("Onay", f"{ad} isimli hasta ve TÜM verileri silinecek?"):
            try:
                conn = baglan(); cursor = conn.cursor()
                cursor.execute("DELETE FROM Hastalar WHERE HastaID = %s", (id,))
                conn.commit(); conn.close()
                log_tut("HASTA SİLME", f"Hasta ID:{id} ve tüm verileri silindi.")
                hasta_listele(); istatistikleri_guncelle(); combobox_guncelle()
            except mysql.connector.Error as err: messagebox.showerror("Hata", f"Silinemedi:\n{err}")

    def hasta_verileri_getir():
        secili = tr_hasta.selection()
        if not secili: messagebox.showwarning("Uyarı", "Seçim yapınız"); return
        vals = tr_hasta.item(secili)['values'] 
        for e in [en_h_ad, en_h_soy, en_h_tc, en_h_tel, en_h_boy, en_h_hedef]: e.delete(0, END)
        en_h_ad.insert(0, vals[1]); en_h_soy.insert(0, vals[2]); en_h_tc.insert(0, str(vals[3]))
        en_h_tel.insert(0, vals[4]); cb_h_cin.set(vals[5]); en_h_boy.insert(0, str(vals[6])); en_h_hedef.insert(0, str(vals[7]))

    def hasta_guncelle():
        secili = tr_hasta.selection()
        if not secili: return
        id = tr_hasta.item(secili)['values'][0]
        try:
            conn = baglan(); cursor = conn.cursor()
            sql = "UPDATE Hastalar SET Ad=%s, Soyad=%s, TCNo=%s, Telefon=%s, Cinsiyet=%s, Boy=%s, HedefKilo=%s WHERE HastaID=%s"
            val = (en_h_ad.get(), en_h_soy.get(), en_h_tc.get(), en_h_tel.get(), cb_h_cin.get(), en_h_boy.get(), en_h_hedef.get(), id)
            cursor.execute(sql, val); conn.commit(); conn.close()
            hasta_listele(); istatistikleri_guncelle(); combobox_guncelle()
            log_tut("GÜNCELLEME", f"Hasta ID:{id} güncellendi.")
            messagebox.showinfo("Başarılı", "Güncellendi")
            for e in [en_h_ad, en_h_soy, en_h_tc, en_h_tel, en_h_boy, en_h_hedef]: e.delete(0, END)
        except Exception as e: messagebox.showerror("Hata", str(e))

    def hasta_listele():
        for i in tr_hasta.get_children(): tr_hasta.delete(i)
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("SELECT HastaID, Ad, Soyad, TCNo, Telefon, Cinsiyet, Boy, HedefKilo FROM Hastalar")
        for r in cursor.fetchall(): tr_hasta.insert("", END, values=r)
        conn.close()

    frm_h = ttk.LabelFrame(t_hasta, text=" Hasta İşlemleri ")
    frm_h.pack(fill="x", padx=20, pady=10)
    Label(frm_h, text="Ad:", bg=RENK_BG).grid(row=0, column=0, padx=5, pady=10)
    en_h_ad = Entry(frm_h); en_h_ad.grid(row=0, column=1)
    Label(frm_h, text="Soyad:", bg=RENK_BG).grid(row=0, column=2, padx=5)
    en_h_soy = Entry(frm_h); en_h_soy.grid(row=0, column=3)
    Label(frm_h, text="TC No:", bg=RENK_BG).grid(row=0, column=4, padx=5)
    en_h_tc = Entry(frm_h); en_h_tc.grid(row=0, column=5)
    Label(frm_h, text="Telefon:", bg=RENK_BG).grid(row=1, column=0, padx=5, pady=10)
    en_h_tel = Entry(frm_h); en_h_tel.grid(row=1, column=1)
    Label(frm_h, text="D.Tarihi:", bg=RENK_BG).grid(row=1, column=2, padx=5)
    en_h_dt = Entry(frm_h); en_h_dt.insert(0, "1990-01-01"); en_h_dt.grid(row=1, column=3)
    Label(frm_h, text="Cinsiyet:", bg=RENK_BG).grid(row=1, column=4, padx=5)
    cb_h_cin = ttk.Combobox(frm_h, values=["K", "E"], width=17); cb_h_cin.grid(row=1, column=5)
    Label(frm_h, text="Boy (cm):", bg=RENK_BG).grid(row=2, column=0, padx=5, pady=10)
    en_h_boy = Entry(frm_h); en_h_boy.grid(row=2, column=1)
    Label(frm_h, text="Hedef Kilo:", bg=RENK_BG).grid(row=2, column=2, padx=5)
    en_h_hedef = Entry(frm_h); en_h_hedef.grid(row=2, column=3)

    Button(frm_h, text="💾 KAYDET", command=hasta_kaydet, bg=RENK_BTN_SUCCESS, fg="white", font=FONT_BOLD).grid(row=2, column=4, padx=5)
    Button(frm_h, text="🗑️ SİL", command=hasta_sil, bg=RENK_BTN_DANGER, fg="white", font=FONT_BOLD).grid(row=2, column=5, padx=5)
    Button(frm_h, text="✏️ ÇEK", command=hasta_verileri_getir, bg=RENK_BTN_WARNING).grid(row=2, column=6, padx=5)
    Button(frm_h, text="🔄 GÜNCELLE", command=hasta_guncelle, bg=RENK_ACCENT, fg="white").grid(row=2, column=7, padx=5)

    tr_hasta = ttk.Treeview(t_hasta, columns=("ID", "Ad", "Soyad", "TC", "Tel", "Cins", "Boy", "Hedef"), show="headings")
    for c in ("ID", "Ad", "Soyad", "TC", "Tel", "Cins", "Boy", "Hedef"): tr_hasta.heading(c, text=c)
    tr_hasta.pack(fill="both", expand=True, padx=20, pady=10)

    # --- TAB 2: HASTALIKLAR ---
    def hastalik_ekle():
        if not en_hst_ad.get(): return
        conn = baglan(); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO TanimliHastaliklar (HastalikAdi, RiskSeviyesi) VALUES (%s, 1)", (en_hst_ad.get(),))
            conn.commit()
            log_tut("HASTALIK EKLE", f"Yeni hastalık: {en_hst_ad.get()}")
            hastalik_listele(); combobox_guncelle(); en_hst_ad.delete(0, END)
            messagebox.showinfo("Başarılı", "Eklendi")
        except Exception as e: messagebox.showerror("Hata", str(e))
        finally: conn.close()

    def hastalik_ata():
        if not cb_hst_hasta.get() or not cb_hst_hastalik.get(): return
        h_id = cb_hst_hasta.get().split("ID: ")[1].replace(")","")
        d_id = cb_hst_hastalik.get().split("ID: ")[1].replace(")","")
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("INSERT INTO HastaHastaliklari (HastaID, HastalikID, TeshisTarihi) VALUES (%s, %s, NOW())", (h_id, d_id))
        conn.commit(); conn.close()
        log_tut("TANI EKLEME", f"Hasta ID:{h_id} -> Hastalık ID:{d_id}")
        hastalik_listele()

    def hastalik_listele():
        for i in tr_hst.get_children(): tr_hst.delete(i)
        conn = baglan(); cursor = conn.cursor()
        sql = "SELECT H.Ad, H.Soyad, T.HastalikAdi, HH.TeshisTarihi FROM HastaHastaliklari HH JOIN Hastalar H ON HH.HastaID=H.HastaID JOIN TanimliHastaliklar T ON HH.HastalikID=T.HastalikID"
        cursor.execute(sql)
        for r in cursor.fetchall(): tr_hst.insert("", END, values=r)
        conn.close()

    fr_hst = Frame(t_saglik, bg=RENK_BG); fr_hst.pack(fill="x", padx=20, pady=10)
    p1 = ttk.LabelFrame(fr_hst, text="Hastalık Tanımla"); p1.pack(side="left", fill="both", expand=True, padx=5)
    en_hst_ad = Entry(p1); en_hst_ad.pack(pady=5, padx=5, fill="x")
    Button(p1, text="➕ EKLE", command=hastalik_ekle, bg=RENK_BTN_WARNING).pack(pady=5)
    
    p2 = ttk.LabelFrame(fr_hst, text="Hastaya Hastalık Ata"); p2.pack(side="right", fill="both", expand=True, padx=5)
    cb_hst_hasta = ttk.Combobox(p2); cb_hst_hasta.pack(pady=5, padx=5, fill="x")
    cb_hst_hastalik = ttk.Combobox(p2); cb_hst_hastalik.pack(pady=5, padx=5, fill="x")
    Button(p2, text="🔗 EŞLEŞTİR", command=hastalik_ata, bg=RENK_ACCENT, fg="white").pack(pady=5)
    tr_hst = ttk.Treeview(t_saglik, columns=("Ad", "Soyad", "Hastalık", "Tarih"), show="headings")
    for c in ("Ad", "Soyad", "Hastalık", "Tarih"): tr_hst.heading(c, text=c)
    tr_hst.pack(fill="both", expand=True, padx=20, pady=10)

    # --- TAB 3: BESİNLER ---
    def besin_ekle():
        if not en_b_ad.get(): return
        conn = baglan(); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Besinler (BesinAdi, Kalori, Protein, Karbonhidrat, Yag) VALUES (%s,%s,%s,%s,%s)",
                           (en_b_ad.get(), en_b_kal.get(), en_b_pro.get(), en_b_kar.get(), en_b_yag.get()))
            conn.commit()
            log_tut("BESİN EKLE", f"Besin Eklendi: {en_b_ad.get()}")
            besin_listele(); combobox_guncelle(); istatistikleri_guncelle()
            for e in [en_b_ad, en_b_kal, en_b_pro, en_b_kar, en_b_yag]: e.delete(0, END)
            messagebox.showinfo("Başarılı", "Eklendi")
        except Exception as e: messagebox.showerror("Hata", str(e))
        finally: conn.close()

    def besin_sil():
        secili = tr_besin.selection()
        if not secili: return
        ad = tr_besin.item(secili)['values'][0]
        if messagebox.askyesno("Onay", f"{ad} silinecek?"):
            conn = baglan(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Besinler WHERE BesinAdi = %s", (ad,))
            conn.commit(); conn.close()
            log_tut("BESİN SİLME", f"{ad} silindi.")
            besin_listele()

    def besin_cek():
        secili = tr_besin.selection()
        if not secili: return
        v = tr_besin.item(secili)['values']
        for e in [en_b_ad, en_b_kal, en_b_pro, en_b_kar, en_b_yag]: e.delete(0, END)
        en_b_ad.insert(0, v[0]); en_b_kal.insert(0, v[1]); en_b_pro.insert(0, v[2])
        en_b_kar.insert(0, v[3]); en_b_yag.insert(0, v[4])

    def besin_guncelle():
        s = tr_besin.selection()
        if not s: return
        eski_ad = tr_besin.item(s)['values'][0]
        conn = baglan(); cursor = conn.cursor()
        sql = "UPDATE Besinler SET BesinAdi=%s, Kalori=%s, Protein=%s, Karbonhidrat=%s, Yag=%s WHERE BesinAdi=%s"
        val = (en_b_ad.get(), en_b_kal.get(), en_b_pro.get(), en_b_kar.get(), en_b_yag.get(), eski_ad)
        cursor.execute(sql, val); conn.commit(); conn.close()
        log_tut("BESİN GÜNCELLE", f"{eski_ad} güncellendi.")
        besin_listele(); messagebox.showinfo("OK", "Güncellendi")
        for e in [en_b_ad, en_b_kal, en_b_pro, en_b_kar, en_b_yag]: e.delete(0, END)

    def besin_listele():
        for i in tr_besin.get_children(): tr_besin.delete(i)
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("SELECT BesinAdi, Kalori, Protein, Karbonhidrat, Yag FROM Besinler")
        for r in cursor.fetchall(): tr_besin.insert("", END, values=r)
        conn.close()

    frm_b = ttk.LabelFrame(t_besin, text=" Besin Kütüphanesi ")
    frm_b.pack(fill="x", padx=20, pady=10)
    Label(frm_b, text="Ad:", bg=RENK_BG).grid(row=0, column=0, padx=5)
    en_b_ad = Entry(frm_b, width=20); en_b_ad.grid(row=0, column=1)
    Label(frm_b, text="Kalori:", bg=RENK_BG).grid(row=0, column=2, padx=5)
    en_b_kal = Entry(frm_b, width=10); en_b_kal.grid(row=0, column=3)
    Label(frm_b, text="P/K/Y:", bg=RENK_BG).grid(row=0, column=4, padx=5)
    en_b_pro = Entry(frm_b, width=5); en_b_pro.grid(row=0, column=5)
    en_b_kar = Entry(frm_b, width=5); en_b_kar.grid(row=0, column=6)
    en_b_yag = Entry(frm_b, width=5); en_b_yag.grid(row=0, column=7)
    
    Button(frm_b, text="➕ EKLE", command=besin_ekle, bg=RENK_BTN_SUCCESS, fg="white").grid(row=0, column=8, padx=5)
    Button(frm_b, text="🗑️ SİL", command=besin_sil, bg=RENK_BTN_DANGER, fg="white").grid(row=0, column=9, padx=5)
    Button(frm_b, text="✏️ ÇEK", command=besin_cek, bg=RENK_BTN_WARNING).grid(row=0, column=10, padx=5)
    Button(frm_b, text="🔄 GÜNCELLE", command=besin_guncelle, bg=RENK_ACCENT, fg="white").grid(row=0, column=11, padx=5)
    
    tr_besin = ttk.Treeview(t_besin, columns=("Ad", "Kalori", "Pro", "Karb", "Yag"), show="headings")
    for c in ("Ad", "Kalori", "Pro", "Karb", "Yag"): tr_besin.heading(c, text=c)
    tr_besin.pack(fill="both", expand=True, padx=20, pady=10)

    # --- TAB 4: DİYET YAZMA & PDF ---
    def program_olustur():
        if not cb_dyt_hasta.get(): return
        h_id = cb_dyt_hasta.get().split("ID: ")[1].replace(")","")
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("INSERT INTO DiyetProgramlari (HastaID, BaslangicTarihi, Aciklama) VALUES (%s, NOW(), %s)", (h_id, en_dyt_not.get()))
        conn.commit(); conn.close(); program_listele(); log_tut("DİYET", "Program oluşturuldu")

    def program_sil():
        secili = lb_prog.curselection()
        if not secili: return
        prog_id = lb_prog.get(secili).split("PrgID: ")[1].split(" |")[0]
        if messagebox.askyesno("Onay", "Program ve yemekler silinecek?"):
            conn = baglan(); cursor = conn.cursor()
            cursor.execute("DELETE FROM DiyetProgramlari WHERE ProgramID = %s", (prog_id,))
            conn.commit(); conn.close(); program_listele(); log_tut("PROG SİL", f"ID:{prog_id} silindi")

    def program_listele():
        lb_prog.delete(0, END)
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("SELECT P.ProgramID, H.Ad, H.Soyad, P.Aciklama FROM DiyetProgramlari P JOIN Hastalar H ON P.HastaID=H.HastaID ORDER BY P.ProgramID DESC")
        for r in cursor.fetchall(): lb_prog.insert(END, f"PrgID: {r[0]} | {r[1]} {r[2]} - {r[3]}")
        conn.close()

    def yemek_ekle():
        if not lb_prog.curselection(): messagebox.showwarning("Hata", "Program seçin!"); return
        secili_prog = lb_prog.get(ACTIVE).split("PrgID: ")[1].split(" |")[0]
        b_id = cb_dyt_besin.get().split("ID: ")[1].replace(")","")
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("INSERT INTO DiyetDetaylari (ProgramID, BesinID, Gun, Ogun, Miktar) VALUES (%s,%s,%s,%s,%s)",
                       (secili_prog, b_id, cb_dyt_gun.get(), cb_dyt_ogun.get(), en_dyt_miktar.get()))
        conn.commit(); conn.close()
        log_tut("DİYET YEMEK", f"Prg:{secili_prog} Besin:{b_id} Eklendi")
        messagebox.showinfo("Bilgi", "Yemek Eklendi"); en_dyt_miktar.delete(0, END)

    def program_analiz_et():
        if not lb_prog.curselection(): return
        prog_id = lb_prog.get(ACTIVE).split("PrgID: ")[1].split(" |")[0]
        try:
            conn = baglan(); cursor = conn.cursor()
            cursor.callproc('Program_Analizi', [prog_id])
            for result in cursor.stored_results():
                r = result.fetchone()
                if r and r[0] is not None:
                    m = f"Toplam Kalori: {r[0]:.2f}\nProtein: {r[1]:.2f}\nKarb: {r[2]:.2f}\nYağ: {r[3]:.2f}"
                    messagebox.showinfo("Program Özeti", m)
                    log_tut("ANALİZ", f"Prg:{prog_id} analiz edildi.")
                else: messagebox.showinfo("Bilgi", "Yemek yok")
            conn.close()
        except: pass

    def program_icerigi_goster():
        secili = lb_prog.curselection()
        if not secili: messagebox.showwarning("Uyarı", "Program seçin"); return
        prog_info = lb_prog.get(secili); prog_id = prog_info.split("PrgID: ")[1].split(" |")[0]
        pen = Toplevel(); pen.title("Diyet Listesi"); pen.geometry("700x500"); pen.configure(bg=RENK_BG)
        Label(pen, text=f"{prog_info}\nListesi", bg=RENK_BG, font=FONT_HEADER, fg=RENK_MENU).pack(pady=10)
        tr = ttk.Treeview(pen, columns=("Gün", "Öğün", "Besin", "Miktar", "Kalori"), show="headings")
        tr.heading("Gün", text="Gün"); tr.heading("Öğün", text="Öğün"); tr.heading("Besin", text="Besin")
        tr.heading("Miktar", text="Miktar"); tr.heading("Kalori", text="Kalori")
        tr.pack(fill="both", expand=True, padx=20)
        conn = baglan(); cursor = conn.cursor()
        sql = """SELECT D.Gun, D.Ogun, B.BesinAdi, D.Miktar, (B.Kalori * D.Miktar) 
                 FROM DiyetDetaylari D JOIN Besinler B ON D.BesinID = B.BesinID WHERE D.ProgramID = %s 
                 ORDER BY FIELD(D.Gun,'Pazartesi','Salı','Çarşamba','Perşembe','Cuma','C.tesi','Pazar'), 
                 FIELD(D.Ogun,'Sabah','Öğle','Ara Öğün','Akşam')"""
        cursor.execute(sql, (prog_id,))
        for r in cursor.fetchall(): tr.insert("", END, values=r)
        conn.close()

    def diyet_pdf_al():
        if not PDF_AKTIF: messagebox.showerror("Hata", "reportlab kütüphanesi yüklü değil!"); return
        if not lb_prog.curselection(): messagebox.showwarning("Uyarı", "Program Seçin"); return
        prog_info = lb_prog.get(ACTIVE)
        prog_id = prog_info.split("PrgID: ")[1].split(" |")[0]
        dosya_adi = f"DiyetProgrami_{prog_id}.pdf"
        try:
            conn = baglan(); cursor = conn.cursor()
            cursor.execute("SELECT * FROM DiyetDetaylari D JOIN Besinler B ON D.BesinID=B.BesinID WHERE D.ProgramID=%s", (prog_id,))
            veriler = cursor.fetchall(); conn.close()
            c = canvas.Canvas(dosya_adi, pagesize=A4); c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 800, tr_duzelt(f"DIYET PROGRAMI - ID: {prog_id}"))
            c.setFont("Helvetica", 12); c.drawString(50, 780, tr_duzelt(f"Hasta/Detay: {prog_info}")); c.line(50, 770, 550, 770)
            y = 740; c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "GUN"); c.drawString(150, y, "OGUN"); c.drawString(250, y, "BESIN"); c.drawString(400, y, "MIKTAR")
            y -= 20; c.setFont("Helvetica", 10)
            for v in veriler:
                if y < 50: c.showPage(); y = 800
                c.drawString(50, y, tr_duzelt(v[2])); c.drawString(150, y, tr_duzelt(v[3]))
                c.drawString(250, y, tr_duzelt(v[6])); c.drawString(400, y, tr_duzelt(str(v[4])))
                y -= 20
            c.save()
            messagebox.showinfo("Başarılı", f"PDF: {os.path.abspath(dosya_adi)}")
            log_tut("PDF", f"Diyet ID:{prog_id} PDF'e aktarıldı.")
        except Exception as e: messagebox.showerror("Hata", str(e))

    fr_d = Frame(t_diyet, bg=RENK_BG); fr_d.pack(fill="both", expand=True, padx=10, pady=10)
    p_sol = ttk.LabelFrame(fr_d, text="1. Adım: Program Başlığı"); p_sol.pack(side="left", fill="both", expand=True, padx=5)
    cb_dyt_hasta = ttk.Combobox(p_sol); cb_dyt_hasta.pack(pady=5, padx=5, fill="x")
    en_dyt_not = Entry(p_sol); en_dyt_not.insert(0, "Program Notu..."); en_dyt_not.pack(pady=5, padx=5, fill="x")
    Button(p_sol, text="OLUŞTUR", command=program_olustur, bg=RENK_MENU, fg="white").pack(pady=5, fill="x", padx=5)
    Button(p_sol, text="SEÇİLİ PROGRAMI SİL", command=program_sil, bg=RENK_BTN_DANGER, fg="white").pack(pady=5, fill="x", padx=5)
    Button(p_sol, text="📊 KALORİ ANALİZİ", command=program_analiz_et, bg="#8E44AD", fg="white").pack(pady=5, fill="x", padx=5)
    Button(p_sol, text="📄 LİSTEYİ GÖR", command=program_icerigi_goster, bg="#16A085", fg="white").pack(pady=5, fill="x", padx=5)
    Button(p_sol, text="📄 PDF OLARAK İNDİR", command=diyet_pdf_al, bg="#C0392B", fg="white").pack(pady=20, fill="x", padx=5)
    lb_prog = Listbox(p_sol, bg="#ECF0F1"); lb_prog.pack(fill="both", expand=True, padx=5, pady=5)
    
    p_sag = ttk.LabelFrame(fr_d, text="2. Adım: Yemek Ekle"); p_sag.pack(side="right", fill="both", expand=True, padx=5)
    Label(p_sag, text="Besin:", bg=RENK_BG).pack(anchor="w", padx=5)
    cb_dyt_besin = ttk.Combobox(p_sag); cb_dyt_besin.pack(fill="x", padx=5)
    Label(p_sag, text="Gün/Öğün:", bg=RENK_BG).pack(anchor="w", padx=5)
    cb_dyt_gun = ttk.Combobox(p_sag, values=["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "C.tesi", "Pazar"]); cb_dyt_gun.pack(fill="x", padx=5)
    cb_dyt_ogun = ttk.Combobox(p_sag, values=["Sabah", "Öğle", "Akşam", "Ara Öğün"]); cb_dyt_ogun.pack(fill="x", padx=5)
    Label(p_sag, text="Miktar:", bg=RENK_BG).pack(anchor="w", padx=5)
    en_dyt_miktar = Entry(p_sag); en_dyt_miktar.pack(fill="x", padx=5)
    Button(p_sag, text="➕ YEMEĞİ EKLE", command=yemek_ekle, bg=RENK_BTN_SUCCESS, fg="white").pack(pady=20, fill="x", padx=20)

    # --- TAB 5: TAKİP ---
    def rapor_al_stored_proc():
        if not cb_tkp_hasta.get(): return
        h_id = cb_tkp_hasta.get().split("ID: ")[1].replace(")","")
        try:
            conn = baglan(); cursor = conn.cursor()
            cursor.callproc('Hasta_Raporu_Getir', [h_id])
            rapor = ""
            for result in cursor.stored_results():
                r = result.fetchone()
                if r: rapor = f"HASTA: {r[0]} {r[1]}\nTEL: {r[2]}\nVKI: {r[3]}\nTOPLAM SU: {r[4]} Lt"
            
            cursor.execute("SELECT Kilo FROM Olcumler WHERE HastaID=%s ORDER BY Tarih DESC LIMIT 1", (h_id,))
            son = cursor.fetchone()
            if son:
                cursor.execute("SELECT Kalori_Ihtiyaci_Hesapla(%s, Boy, 30, Cinsiyet) FROM Hastalar WHERE HastaID=%s", (son[0], h_id))
                rapor += f"\n\nGÜNLÜK KALORİ İHTİYACI: {cursor.fetchone()[0]} kcal"
            
            messagebox.showinfo("Rapor", rapor); log_tut("RAPOR", f"Hasta ID:{h_id} raporlandı."); conn.close()
        except mysql.connector.Error as e: messagebox.showerror("Hata", str(e))

    def veri_kaydet(tip):
        if not cb_tkp_hasta.get(): messagebox.showwarning("Uyarı", "Hasta seçin"); return
        h_id = cb_tkp_hasta.get().split("ID: ")[1].replace(")","")
        conn = baglan(); cursor = conn.cursor()
        try:
            if tip == "SU":
                if not en_su.get(): return
                cursor.execute("INSERT INTO SuTakibi (HastaID, Tarih, HedefLitre, IcilenLitre) VALUES (%s, NOW(), 2.5, %s)", (h_id, en_su.get()))
                log_tut("SU GİRİŞİ", f"Hasta ID:{h_id} -> {en_su.get()} Litre")
                en_su.delete(0, END)
            else:
                if not en_kilo.get(): messagebox.showwarning("Uyarı", "Değer girin"); return
                cursor.execute("INSERT INTO Olcumler (HastaID, Tarih, Kilo, BelCevresi, KalcaCevresi) VALUES (%s, NOW(), %s, %s, %s)", 
                               (h_id, en_kilo.get(), en_bel.get(), en_kalca.get()))
                # Ölçümde TRIGGER çalıştığı için log_tut'a gerek yok, otomatik "OTOMATİK" logu atacak.
                # Ama biz manuel de görelim dersen aşağıdaki satırı açabilirsin:
                log_tut("ÖLÇÜM GİRİŞİ", f"Hasta ID:{h_id} Kilo:{en_kilo.get()}")
                for e in [en_kilo, en_bel, en_kalca]: e.delete(0, END)
            conn.commit(); messagebox.showinfo("Bilgi", "Kayıt Başarılı")
        except mysql.connector.Error as err: messagebox.showerror("Hata", str(err))
        finally: conn.close()

    fr_tkp = ttk.LabelFrame(t_takip, text=" Takip Paneli ")
    fr_tkp.pack(padx=20, pady=20, fill="both", expand=True)
    Label(fr_tkp, text="Hasta Seç:", bg=RENK_BG, font=FONT_BOLD).pack(pady=5)
    cb_tkp_hasta = ttk.Combobox(fr_tkp, width=40); cb_tkp_hasta.pack(pady=5)
    Button(fr_tkp, text="📋 GELİŞMİŞ RAPOR GETİR", command=rapor_al_stored_proc, bg=RENK_BTN_WARNING).pack(pady=10)
    
    f_sub = Frame(fr_tkp, bg=RENK_BG); f_sub.pack(fill="both", expand=True)
    f_su = Frame(f_sub, bg="white", bd=1, relief="solid"); f_su.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    Label(f_su, text="SU TAKİBİ", font=FONT_BOLD, bg="white").pack(pady=5)
    Label(f_su, text="Litre:", bg="white").pack(); en_su = Entry(f_su, justify="center"); en_su.pack(pady=5)
    Button(f_su, text="KAYDET", command=lambda: veri_kaydet("SU"), bg=RENK_ACCENT, fg="white").pack(pady=10)
    
    f_ol = Frame(f_sub, bg="white", bd=1, relief="solid"); f_ol.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    Label(f_ol, text="ÖLÇÜMLER", font=FONT_BOLD, bg="white").pack(pady=5)
    Label(f_ol, text="Kilo:", bg="white").pack(); en_kilo = Entry(f_ol, justify="center"); en_kilo.pack()
    Label(f_ol, text="Bel:", bg="white").pack(); en_bel = Entry(f_ol, justify="center"); en_bel.pack()
    Label(f_ol, text="Kalça:", bg="white").pack(); en_kalca = Entry(f_ol, justify="center"); en_kalca.pack()
    Button(f_ol, text="KAYDET", command=lambda: veri_kaydet("OLCUM"), bg="#9B59B6", fg="white").pack(pady=10)

    # --- TAB 6: RANDEVU ---
    def randevu_ver():
        if not cb_rnd_hasta.get(): return
        h_id = cb_rnd_hasta.get().split("ID: ")[1].replace(")","")
        conn = baglan(); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Randevular (HastaID, TarihSaat, Durum) VALUES (%s, %s, 1)", (h_id, en_rnd_trh.get()))
            conn.commit(); log_tut("RANDEVU", f"Hasta ID:{h_id} randevu verildi.")
            randevu_listele(); istatistikleri_guncelle()
        except mysql.connector.Error as e: messagebox.showerror("Hata", str(e))
        finally: conn.close()

    def randevu_iptal():
        secili = tr_rnd.selection()
        if not secili: return
        r_id = tr_rnd.item(secili)['values'][0]
        if messagebox.askyesno("Onay", "Randevu iptal edilecek?"):
            conn = baglan(); cursor = conn.cursor()
            cursor.execute("DELETE FROM Randevular WHERE RandevuID = %s", (r_id,))
            conn.commit(); conn.close()
            log_tut("RANDEVU İPTAL", f"ID:{r_id} iptal edildi.")
            randevu_listele(); istatistikleri_guncelle()

    def randevu_cek():
        secili = tr_rnd.selection()
        if not secili: return
        tarih = tr_rnd.item(secili)['values'][3]
        en_rnd_trh.delete(0, END); en_rnd_trh.insert(0, tarih)

    def randevu_guncelle():
        secili = tr_rnd.selection()
        if not secili: return
        r_id = tr_rnd.item(secili)['values'][0]
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("UPDATE Randevular SET TarihSaat=%s WHERE RandevuID=%s", (en_rnd_trh.get(), r_id))
        conn.commit(); conn.close(); randevu_listele()
        log_tut("RANDEVU GÜNCELLE", f"ID:{r_id} tarih değiştirildi.")
        messagebox.showinfo("OK","Güncellendi")
        en_rnd_trh.delete(0, END); en_rnd_trh.insert(0, "2025-12-30 14:00")

    def randevu_listele():
        for i in tr_rnd.get_children(): tr_rnd.delete(i)
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("SELECT R.RandevuID, H.Ad, H.Soyad, R.TarihSaat FROM Randevular R JOIN Hastalar H ON R.HastaID=H.HastaID WHERE R.TarihSaat >= NOW() ORDER BY R.TarihSaat")
        for r in cursor.fetchall(): tr_rnd.insert("", END, values=r)
        conn.close()

    fr_rnd = ttk.LabelFrame(t_randevu, text=" Randevu Paneli ")
    fr_rnd.pack(fill="x", padx=20, pady=10)
    Label(fr_rnd, text="Hasta:", bg=RENK_BG).pack(side="left", padx=5)
    cb_rnd_hasta = ttk.Combobox(fr_rnd, width=25); cb_rnd_hasta.pack(side="left")
    Label(fr_rnd, text="Tarih:", bg=RENK_BG).pack(side="left", padx=5)
    en_rnd_trh = Entry(fr_rnd); en_rnd_trh.insert(0, "2025-12-30 14:00"); en_rnd_trh.pack(side="left")
    Button(fr_rnd, text="VER", command=randevu_ver, bg=RENK_MENU, fg="white").pack(side="left", padx=5)
    Button(fr_rnd, text="İPTAL", command=randevu_iptal, bg=RENK_BTN_DANGER, fg="white").pack(side="left", padx=5)
    Button(fr_rnd, text="✏️ ÇEK", command=randevu_cek, bg=RENK_BTN_WARNING).pack(side="left", padx=5)
    Button(fr_rnd, text="🔄 GÜNCELLE", command=randevu_guncelle, bg=RENK_ACCENT, fg="white").pack(side="left", padx=5)
    
    tr_rnd = ttk.Treeview(t_randevu, columns=("ID", "Ad", "Soyad", "Tarih"), show="headings")
    for c in ("ID", "Ad", "Soyad", "Tarih"): tr_rnd.heading(c, text=c)
    tr_rnd.pack(fill="both", expand=True, padx=20, pady=10)

    # --- TAB 7: LOGLAR ---
    def loglari_getir():
        for i in tr_log.get_children(): tr_log.delete(i)
        conn = baglan(); cursor = conn.cursor()
        cursor.execute("SELECT LogID, Tarih, IslemTipi, Aciklama FROM SistemLoglari ORDER BY LogID DESC LIMIT 50")
        for r in cursor.fetchall(): tr_log.insert("", END, values=r)
        conn.close()

    Button(t_log, text="🔄 YENİLE", command=loglari_getir, bg=RENK_MENU, fg="white").pack(pady=10)
    tr_log = ttk.Treeview(t_log, columns=("ID", "Tarih", "Tip", "Açıklama"), show="headings")
    tr_log.heading("ID", text="ID"); tr_log.column("ID", width=50)
    tr_log.heading("Tarih", text="Tarih"); tr_log.column("Tarih", width=150)
    tr_log.heading("Tip", text="Tip"); tr_log.column("Tip", width=100)
    tr_log.heading("Açıklama", text="Detay"); tr_log.column("Açıklama", width=400)
    tr_log.pack(fill="both", expand=True, padx=20, pady=10)

    # --- BAŞLATMA ---
    def combobox_guncelle():
        try:
            conn = baglan()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("SELECT HastaID, Ad, Soyad FROM Hastalar")
            h = [f"{r[1]} {r[2]} (ID: {r[0]})" for r in cursor.fetchall()]
            cb_h_cin['values'] = ["K", "E"]
            cb_hst_hasta['values'] = h; cb_dyt_hasta['values'] = h; cb_tkp_hasta['values'] = h; cb_rnd_hasta['values'] = h
            cursor.execute("SELECT BesinID, BesinAdi FROM Besinler")
            cb_dyt_besin['values'] = [f"{r[1]} (ID: {r[0]})" for r in cursor.fetchall()]
            cursor.execute("SELECT HastalikID, HastalikAdi FROM TanimliHastaliklar")
            cb_hst_hastalik['values'] = [f"{r[1]} (ID: {r[0]})" for r in cursor.fetchall()]
            conn.close()
        except: pass

    try:
        hasta_listele(); besin_listele(); hastalik_listele(); program_listele(); randevu_listele(); loglari_getir()
        combobox_guncelle(); istatistikleri_guncelle()
    except: pass
    
    root.mainloop()

if __name__ == "__main__":
    giris_ekrani()