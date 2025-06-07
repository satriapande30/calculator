import customtkinter as ctk
import math
import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
import requests
from threading import Thread
import time

class CurrencyConverter:
    """Handler untuk konversi mata uang dengan API real-time"""
    
    def __init__(self):
        # API Key untuk ExchangeRate-API (gratis)
        # Daftar di: https://app.exchangerate-api.com/sign-up/free
        # Ganti dengan API key Anda sendiri
        self.api_key = "d14ebfc4b79f612afe151532"  # GANTI DENGAN API KEY ANDA
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}"
        self.rates = {}
        self.last_update = 0
        self.update_interval = 3600  # Update setiap 1 jam
        
    def fetch_rates(self):
        """Mengambil rate mata uang dari API"""
        try:
            response = requests.get(f"{self.base_url}/latest/USD", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['result'] == 'success':
                    self.rates = data['conversion_rates']
                    self.last_update = time.time()
                    return True
            return False
        except Exception as e:
            print(f"Error fetching currency rates: {e}")
            return False
    
    def convert(self, amount, from_currency, to_currency):
        """Konversi mata uang"""
        # Cek apakah perlu update rates
        if time.time() - self.last_update > self.update_interval or not self.rates:
            if not self.fetch_rates():
                raise Exception("Tidak dapat mengambil data kurs mata uang. Periksa koneksi internet.")
        
        if from_currency not in self.rates or to_currency not in self.rates:
            raise Exception("Mata uang tidak didukung")
        
        # Konversi melalui USD sebagai base
        usd_amount = amount / self.rates[from_currency]
        result = usd_amount * self.rates[to_currency]
        return result

class UnitConverter:
    """Kelas untuk menangani konversi berbagai satuan"""
    
    def __init__(self):
        self.currency_converter = CurrencyConverter()
        
        # Definisi konversi untuk setiap kategori (semua ke unit base)
        self.conversions = {
            'length': {
                'meter': 1.0,
                'kilometer': 1000.0,
                'feet': 0.3048,
                'inch': 0.0254,
                'mile': 1609.34
            },
            'weight': {
                'kilogram': 1.0,
                'gram': 0.001,
                'pound': 0.453592,
                'ounce': 0.0283495
            },
            'temperature': {
                # Suhu memerlukan penanganan khusus
                'celsius': 0,
                'fahrenheit': 1,
                'kelvin': 2
            },
            'volume': {
                'liter': 1.0,
                'gallon': 3.78541,
                'milliliter': 0.001
            },
            'currency': {
                'USD': 'USD',
                'EUR': 'EUR',
                'JPY': 'JPY',
                'GBP': 'GBP',
                'AUD': 'AUD',
                'CAD': 'CAD',
                'CHF': 'CHF',
                'CNY': 'CNY',
                'SEK': 'SEK',
                'NZD': 'NZD',
                'MXN': 'MXN',
                'SGD': 'SGD',
                'HKD': 'HKD',
                'NOK': 'NOK',
                'IDR': 'IDR'
            },
            'energy': {
                'joule': 1.0,
                'calorie': 4.184,
                'btu': 1055.06
            }
        }
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Konversi suhu dengan formula khusus"""
        # Convert to Celsius first
        if from_unit == 'fahrenheit':
            celsius = (value - 32) * 5/9
        elif from_unit == 'kelvin':
            celsius = value - 273.15
        else:  # celsius
            celsius = value
        
        # Convert from Celsius to target
        if to_unit == 'fahrenheit':
            return celsius * 9/5 + 32
        elif to_unit == 'kelvin':
            return celsius + 273.15
        else:  # celsius
            return celsius
    
    def convert(self, value, from_unit, to_unit, category):
        """Konversi umum untuk semua kategori kecuali suhu dan mata uang"""
        if category == 'temperature':
            return self.convert_temperature(value, from_unit, to_unit)
        elif category == 'currency':
            return self.currency_converter.convert(value, from_unit, to_unit)
        else:
            # Konversi standar: ke base unit kemudian ke target unit
            base_value = value * self.conversions[category][from_unit]
            result = base_value / self.conversions[category][to_unit]
            return result

class FinancialCalculator(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_calc = tk.StringVar(value="compound")
        self.create_selector()
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=4, pady=4)
        self.render_calculator()

    def create_selector(self):
        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(pady=10, fill="x")
        options = [
            ("Compound Interest", "compound"),
            ("Loan Calculator", "loan"),
            ("Percentage Calc", "percent"),
            ("Break-even", "bep"),
            ("ROI", "roi"),
        ]
        for name, val in options:
            btn = ctk.CTkButton(selector_frame, text=name, width=110, fg_color=None,
                                command=lambda v=val: self.switch_calc(v))
            btn.pack(side='left', padx=4)
    def switch_calc(self, val):
        self.selected_calc.set(val)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.render_calculator()
    def render_calculator(self):
        kind = self.selected_calc.get()
        if kind == "compound":
            self.compound_interest()
        elif kind == "loan":
            self.loan_calculator()
        elif kind == "percent":
            self.percentage_calculator()
        elif kind == "bep":
            self.bep_calculator()
        elif kind == "roi":
            self.roi_calculator()
    # --- 1. Compound Interest ---
    def compound_interest(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Compound Interest Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        entries = {}
        def field(lbl, key, default=''):
            ctk.CTkLabel(frame, text=lbl).pack()
            ent = ctk.CTkEntry(frame)
            ent.insert(0, default)
            ent.pack()
            entries[key] = ent
        field("Principal (Rp)", 'p')
        field("Annual Rate (%)", 'r')
        field("Years", 't')
        field("Compounded per Year (n)", 'n', default='1')
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=8)
        def hitung():
            try:
                p = float(entries['p'].get())
                r = float(entries['r'].get())
                t = float(entries['t'].get())
                n = int(entries['n'].get())
                if p < 0 or r < 0 or t < 0 or n < 1:
                    raise ValueError
                a = p*(1+(r/100)/n)**(n*t)
                output.configure(text="Akhir: Rp {:.2f}\nTotal Bunga: Rp {:.2f}".format(a, a-p))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack(pady=(6,2))
        ctk.CTkLabel(frame, text="A = P(1+r/n)^(nt)").pack()
    # --- 2. Loan Calculator ---
    def loan_calculator(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Loan Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        entries = {}
        def field(lbl, key):
            ctk.CTkLabel(frame, text=lbl).pack()
            ent = ctk.CTkEntry(frame); ent.pack()
            entries[key] = ent
        field("Jumlah Pinjaman (Rp)", "principal")
        field("Tenor/Pokok (bulan)", "periods")
        field("Bunga tetap /tahun (%)", "rate")
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=8)
        def hitung():
            try:
                P = float(entries['principal'].get())
                n = int(entries['periods'].get())
                r = float(entries['rate'].get())
                if P <= 0 or r < 0 or n < 1: raise ValueError
                rm = r/100/12
                if rm == 0:
                    angs = P/n
                else:
                    angs = P * rm * (1+rm)**n / ((1+rm)**n-1)
                tot = angs*n
                output.configure(text="Cicilan/bln: Rp {:.2f}\nTotal Bayar: Rp {:.2f}\nTotal Bunga: Rp {:.2f}".format(
                    angs, tot, tot-P))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack(pady=(6,2))
        ctk.CTkLabel(frame, text="Formula: annuity/amortisasi").pack()
    # --- 3. Percentage Calculator ---
    def percentage_calculator(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Percentage Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        # tab mini: mark up, discount, tax
        opt = tk.StringVar(value="markup")
        tabf = ctk.CTkFrame(frame); tabf.pack(pady=2)
        for name, v in [("Markup", "markup"), ("Discount", "disc"), ("Tax", "tax")]:
            ctk.CTkButton(tabf, text=name, width=80, fg_color=None, command=lambda x=v:opt.set(x)).pack(side="left", padx=2)
        innerf = ctk.CTkFrame(frame); innerf.pack(fill="x", pady=4)
        entries = {}
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=6)
        def show_markup():
            for w in innerf.winfo_children(): w.destroy()
            entries.clear()
            ctk.CTkLabel(innerf, text="Harga Dasar (Rp)").pack(); e1=ctk.CTkEntry(innerf); e1.pack(); entries["base"]=e1
            ctk.CTkLabel(innerf, text="Persen Markup (%)").pack(); e2=ctk.CTkEntry(innerf); e2.pack(); entries["pct"]=e2
        def show_disc():
            for w in innerf.winfo_children(): w.destroy()
            entries.clear()
            ctk.CTkLabel(innerf, text="Harga Awal (Rp)").pack(); e1=ctk.CTkEntry(innerf); e1.pack(); entries["base"]=e1
            ctk.CTkLabel(innerf, text="Persen Diskon (%)").pack(); e2=ctk.CTkEntry(innerf); e2.pack(); entries["pct"]=e2
        def show_tax():
            for w in innerf.winfo_children(): w.destroy()
            entries.clear()
            ctk.CTkLabel(innerf, text="Harga Sebelum Pajak (Rp)").pack(); e1=ctk.CTkEntry(innerf); e1.pack(); entries["base"]=e1
            ctk.CTkLabel(innerf, text="Tax (%)").pack(); e2=ctk.CTkEntry(innerf); e2.pack(); entries["pct"]=e2
        def update_inputs(*_):
            if opt.get()=="markup": show_markup()
            elif opt.get()=="disc": show_disc()
            else: show_tax()
            output.configure(text="")
        opt.trace_add("write", update_inputs)
        update_inputs()
        def hitung():
            try:
                b = float(entries["base"].get())
                p = float(entries["pct"].get())
                if b < 0 or p < 0: raise ValueError
                if opt.get() == "markup":
                    val = b + b*p/100
                    output.configure(text="Harga Jual: Rp {:.2f}".format(val))
                elif opt.get() == "disc":
                    val = b - b*p/100
                    output.configure(text="Setelah Diskon: Rp {:.2f}".format(val))
                else:
                    val = b + b*p/100
                    output.configure(text="Setelah Pajak: Rp {:.2f}".format(val))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack()
    # --- 4. Break-even Point ---
    def bep_calculator(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Break-even Analysis", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        entries = {}
        def field(lbl, key):
            ctk.CTkLabel(frame, text=lbl).pack()
            ent = ctk.CTkEntry(frame); ent.pack()
            entries[key] = ent
        field("Biaya Tetap/Bulan (Rp)", 'fc')
        field("Harga Jual/unit (Rp)", 'price')
        field("Biaya Variabel/unit (Rp)", 'vc')
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=8)
        def hitung():
            try:
                fc = float(entries['fc'].get())
                p = float(entries['price'].get())
                vc = float(entries['vc'].get())
                if p-vc <= 0 or fc < 0 or p < 0 or vc < 0: raise ValueError
                BEP = fc / (p-vc)
                output.configure(text="Break Even: {:.2f} unit".format(BEP))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack(pady=(6,2))
        ctk.CTkLabel(frame, text="BEP = FC/(P-VC)").pack()
    # --- 5. ROI Calculator ---
    def roi_calculator(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="ROI Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        entries = {}
        def field(lbl, key):
            ctk.CTkLabel(frame, text=lbl).pack()
            ent = ctk.CTkEntry(frame); ent.pack()
            entries[key] = ent
        field("Investasi Awal (Rp)", "invest")
        field("Laba Bersih (Rp)", "gain")
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=8)
        def hitung():
            try:
                i = float(entries["invest"].get())
                g = float(entries["gain"].get())
                if i == 0: raise ValueError
                roi = 100*(g-i)/i
                output.configure(text="ROI: {:.2f}%".format(roi))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack(pady=(6,2))
        ctk.CTkLabel(frame, text="ROI = (Gain-Invest)/Invest x 100%").pack() 

class GeometryEngineeringCalculator(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_calc = tk.StringVar(value="area")
        self.create_selector()
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=4, pady=4)
        self.render_calculator()

    def create_selector(self):
        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(pady=10, fill="x")
        options = [
            ("Area", "area"),
            ("Volume", "volume"),
            ("Trigonometri+", "trig"),
            ("Koordinat", "coord"),
            ("Statistik", "stat"),
        ]
        for name, val in options:
            btn = ctk.CTkButton(selector_frame, text=name, width=100, fg_color=None,
                                command=lambda v=val: self.switch_calc(v))
            btn.pack(side='left', padx=4)

    def switch_calc(self, val):
        self.selected_calc.set(val)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.render_calculator()

    def render_calculator(self):
        kind = self.selected_calc.get()
        if kind == "area":
            self.area_calculator()
        elif kind == "volume":
            self.volume_calculator()
        elif kind == "trig":
            self.trigonometry_adv()
        elif kind == "coord":
            self.coord_converter()
        elif kind == "stat":
            self.statistical_functions()

    # 1. Area Calculator
    def area_calculator(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Area Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        opt = tk.StringVar(value="circle")
        tabf = ctk.CTkFrame(frame); tabf.pack(pady=2)
        for name, v in [("Lingkaran", "circle"), ("Segitiga", "triangle"), ("Persegi", "square")]:
            ctk.CTkButton(tabf, text=name, width=80, fg_color=None, command=lambda x=v: opt.set(x)).pack(side="left", padx=2)
        innerf = ctk.CTkFrame(frame); innerf.pack(fill="both", pady=4)
        entries = {}
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=6)
        def show_circle():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Jari-jari (r)").pack(); e=ctk.CTkEntry(innerf); e.pack(); entries["r"]=e
        def show_triangle():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Alas").pack(); ea=ctk.CTkEntry(innerf); ea.pack(); entries["a"]=ea
            ctk.CTkLabel(innerf, text="Tinggi").pack(); et=ctk.CTkEntry(innerf); et.pack(); entries["t"]=et
        def show_square():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Sisi (s)").pack(); e=ctk.CTkEntry(innerf); e.pack(); entries["s"]=e
        def update_inputs(*_):
            if opt.get()=="circle": show_circle()
            elif opt.get()=="triangle": show_triangle()
            else: show_square()
            output.configure(text="")
        opt.trace_add("write", update_inputs)
        update_inputs()
        def hitung():
            try:
                if opt.get() == "circle":
                    r = float(entries["r"].get())
                    if r < 0: raise ValueError
                    res = 3.141592653589793 * r * r
                    output.configure(text="Luas: {:.4f}".format(res))
                elif opt.get() == "triangle":
                    a = float(entries["a"].get())
                    t = float(entries["t"].get())
                    if a < 0 or t<0: raise ValueError
                    res = 0.5 * a * t
                    output.configure(text="Luas: {:.4f}".format(res))
                else:
                    s = float(entries["s"].get())
                    if s < 0: raise ValueError
                    res = s * s
                    output.configure(text="Luas: {:.4f}".format(res))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack()

    # 2. Volume Calculator
    def volume_calculator(self):
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Volume Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        opt = tk.StringVar(value="cube")
        tabf = ctk.CTkFrame(frame); tabf.pack(pady=2)
        for name, v in [("Kubus", "cube"), ("Silinder", "cylinder"), ("Bola", "sphere")]:
            ctk.CTkButton(tabf, text=name, width=80, fg_color=None, command=lambda x=v: opt.set(x)).pack(side="left", padx=2)
        innerf = ctk.CTkFrame(frame); innerf.pack(fill="both", pady=4)
        entries = {}
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=6)
        def show_cube():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Sisi (s)").pack(); e=ctk.CTkEntry(innerf); e.pack(); entries["s"]=e
        def show_cylinder():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Jari-jari (r)").pack(); er=ctk.CTkEntry(innerf); er.pack(); entries["r"]=er
            ctk.CTkLabel(innerf, text="Tinggi (h)").pack(); eh=ctk.CTkEntry(innerf); eh.pack(); entries["h"]=eh
        def show_sphere():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Jari-jari (r)").pack(); e=ctk.CTkEntry(innerf); e.pack(); entries["r"]=e
        def update_inputs(*_):
            if opt.get()=="cube": show_cube()
            elif opt.get()=="cylinder": show_cylinder()
            else: show_sphere()
            output.configure(text="")
        opt.trace_add("write", update_inputs)
        update_inputs()
        def hitung():
            try:
                if opt.get() == "cube":
                    s = float(entries["s"].get())
                    if s < 0: raise ValueError
                    res = s ** 3
                    output.configure(text="Volume: {:.4f}".format(res))
                elif opt.get() == "cylinder":
                    r = float(entries["r"].get())
                    h = float(entries["h"].get())
                    if r < 0 or h < 0: raise ValueError
                    res = 3.141592653589793 * r * r * h
                    output.configure(text="Volume: {:.4f}".format(res))
                else:  # sphere
                    r = float(entries["r"].get())
                    if r < 0: raise ValueError
                    res = 4/3 * 3.141592653589793 * r**3
                    output.configure(text="Volume: {:.4f}".format(res))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack()

    # 3. Trigonometri Lanjutan
    def trigonometry_adv(self):
        import math
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Trigonometri Lanjutan (Inverse)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        opt = tk.StringVar(value="asin")
        tabf = ctk.CTkFrame(frame); tabf.pack(pady=2)
        for name, v in [("asin", "asin"), ("acos", "acos"), ("atan", "atan")]:
            ctk.CTkButton(tabf, text=name, width=80, fg_color=None, command=lambda x=v: opt.set(x)).pack(side="left", padx=2)
        innerf = ctk.CTkFrame(frame); innerf.pack()
        entries = {}
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=6)
        def update_inputs(*_):
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="Input (angka)").pack(); e=ctk.CTkEntry(innerf); e.pack(); entries["x"]=e
            output.configure(text="")
        opt.trace_add("write", update_inputs)
        update_inputs()
        def hitung():
            try:
                x = float(entries["x"].get())
                if opt.get() == "asin":
                    if x < -1 or x > 1: raise ValueError
                    res = math.degrees(math.asin(x))
                    output.configure(text="asin({}) = {:.4f}°".format(x, res))
                elif opt.get() == "acos":
                    if x < -1 or x > 1: raise ValueError
                    res = math.degrees(math.acos(x))
                    output.configure(text="acos({}) = {:.4f}°".format(x, res))
                else:
                    res = math.degrees(math.atan(x))
                    output.configure(text="atan({}) = {:.4f}°".format(x, res))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack()

    # 4. Koordinat Polar-Kartesius
    def coord_converter(self):
        import math
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Koordinat (Polar ↔ Cartesian)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        opt = tk.StringVar(value="p2c")
        tabf = ctk.CTkFrame(frame); tabf.pack(pady=2)
        for name, v in [("Polar → Kartesius", "p2c"), ("Kartesius → Polar", "c2p")]:
            ctk.CTkButton(tabf, text=name, width=120, fg_color=None, command=lambda x=v: opt.set(x)).pack(side="left", padx=2)
        innerf = ctk.CTkFrame(frame); innerf.pack()
        entries = {}
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=6)
        def show_p2c():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="r").pack(); e1=ctk.CTkEntry(innerf); e1.pack(); entries["r"]=e1
            ctk.CTkLabel(innerf, text="θ (deg)").pack(); e2=ctk.CTkEntry(innerf); e2.pack(); entries["theta"]=e2
        def show_c2p():
            for w in innerf.winfo_children(): w.destroy(); entries.clear()
            ctk.CTkLabel(innerf, text="x").pack(); e1=ctk.CTkEntry(innerf); e1.pack(); entries["x"]=e1
            ctk.CTkLabel(innerf, text="y").pack(); e2=ctk.CTkEntry(innerf); e2.pack(); entries["y"]=e2
        def update_inputs(*_):
            if opt.get()=="p2c": show_p2c()
            else: show_c2p()
            output.configure(text="")
        opt.trace_add("write", update_inputs)
        update_inputs()
        def hitung():
            try:
                if opt.get()=="p2c":
                    r = float(entries["r"].get()); th = float(entries["theta"].get())
                    x = r * math.cos(math.radians(th))
                    y = r * math.sin(math.radians(th))
                    output.configure(text="x = {:.4f}, y = {:.4f}".format(x,y))
                else:
                    x = float(entries["x"].get()); y = float(entries["y"].get())
                    r = (x**2 + y**2)**0.5
                    theta = math.degrees(math.atan2(y,x))
                    output.configure(text="r = {:.4f}, θ = {:.2f}°".format(r,theta))
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack()

    # 5. Statistik Dasar
    def statistical_functions(self):
        import statistics
        frame = self.content_frame
        ctk.CTkLabel(frame, text="Statistik Dasar (mean, median, std)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,8))
        ctk.CTkLabel(frame, text="Input data (pisahkan dengan koma)").pack()
        inp = ctk.CTkEntry(frame, width=400); inp.pack()
        output = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        output.pack(pady=8)
        def hitung():
            try:
                data = [float(x.strip()) for x in inp.get().split(',') if x.strip()!=""]
                if len(data)<1: raise ValueError
                mean = statistics.mean(data)
                median = statistics.median(data)
                std = statistics.stdev(data) if len(data)>1 else 0.0
                output.configure(text=f"Mean: {mean:.4f}\nMedian: {median:.4f}\nStd Dev: {std:.4f}")
            except:
                output.configure(text="Input tidak valid.")
        ctk.CTkButton(frame, text="Hitung", command=hitung).pack()

class KeyboardShortcutManager:
    def __init__(self, root, callback_show_history):
        self.root = root
        self.callback_show_history = callback_show_history
        self.shortcut_show_history = "<Control-h>"
        self.bindings = []
        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.clear_bindings()
        self.bindings.append(self.root.bind(self.shortcut_show_history, lambda e: self.callback_show_history()))

    def set_shortcut(self, shortcut):
        self.shortcut_show_history = shortcut
        self.bind_shortcuts()

    def clear_bindings(self):
        for b in self.bindings:
            try:
                self.root.unbind(b)
            except: pass
        self.bindings = []

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, root, keyboard_man):
        super().__init__(master)
        self.root = root
        self.keyboard_manager = keyboard_man
        
        ctk.CTkLabel(self, text="Customization & Usability", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.section_theme()
        self.section_fontsize()
        self.section_keyboard()
        self.section_window()

    # 1. Multiple Themes
    def section_theme(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=6, padx=4)
        ctk.CTkLabel(frame, text="Theme:", anchor="w").pack(side="left", padx=2)
        options = ["Light", "Dark", "Custom Blue", "Custom Yellow"]
        self.theme_var = tk.StringVar(value="Dark")
        optmenu = ctk.CTkOptionMenu(frame, values=options, variable=self.theme_var, command=self.change_theme)
        optmenu.pack(side="left", padx=5)
    
    def change_theme(self, theme):
        if theme == "Light":
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
        elif theme == "Dark":
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
        elif theme == "Custom Blue":
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
        else:  # Custom Yellow
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("green")
            # Optionally, set widget color manually if you want more customization

    # 2. Font Size Accessibility
    def section_fontsize(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=6, padx=4)
        ctk.CTkLabel(frame, text="Font Size:", anchor="w").pack(side="left", padx=2)
        self.fontsize_var = tk.IntVar(value=14)
        slider = ctk.CTkSlider(frame, from_=10, to=30, number_of_steps=20, variable=self.fontsize_var, command=self.fontsize_callback)
        slider.pack(side="left", padx=6)
        ctk.CTkLabel(frame, textvariable=self.fontsize_var, width=40).pack(side="left")
        
    def fontsize_callback(self, v=None):
        # Update default font size for all ctk widgets
        newsize = int(self.fontsize_var.get())
        ctk.set_widget_scaling(newsize/14)  # affects scaling
        # (Optional: propagate to all frames, not only scaling)

    # 3. Keyboard Shortcuts (customizable)
    def section_keyboard(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=6, padx=4)
        ctk.CTkLabel(frame, text="Custom Shortcut:").pack(anchor="w")
        sub = ctk.CTkFrame(frame)
        sub.pack(fill="x", padx=4, pady=2)
        ctk.CTkLabel(sub, text="Show History").pack(side="left", padx=2)
        self.shortcut_var = tk.StringVar(value=self.keyboard_manager.shortcut_show_history)
        e = ctk.CTkEntry(sub, textvariable=self.shortcut_var, width=60); e.pack(side="left")
        save_btn = ctk.CTkButton(sub, text="Simpan", width=50,
                                 command=self.update_shortcut)
        save_btn.pack(side="left", padx=2)
        ctk.CTkLabel(frame, text='Contoh: "<Control-h>"').pack(anchor="w", padx=10)
        
    def update_shortcut(self):
        val = self.shortcut_var.get()
        self.keyboard_manager.set_shortcut(val)
        ctk.CTkLabel(self, text="Shortcut updated!", text_color="green").pack()

    # 4 & 5. Always On Top & Transparency
    def section_window(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=6, padx=4)
        self.always_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(frame, text="Always on Top", variable=self.always_var, command=self.set_always_on_top).pack(side="left")
        self.transp_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(frame, text="Transparency", variable=self.transp_var, command=self.toggle_transparency).pack(side="left", padx=8)
        ctk.CTkLabel(frame, text="(Overlay Mode)").pack(side="left")

    def set_always_on_top(self):
        self.root.wm_attributes("-topmost", self.always_var.get())

    def toggle_transparency(self):
        if self.transp_var.get():
            self.root.attributes("-alpha", 0.85)  # adjust for your taste
        else:
            self.root.attributes("-alpha", 1.0)

class CalculationHistory:
    def __init__(self):
        self.history_file = "calculator_history.json"
        self.calculations = []
        self.load_history()
    
    def add_calculation(self, expression, result, is_pinned=False):
        """Menambahkan perhitungan ke history"""
        calculation = {
            'id': len(self.calculations) + 1,
            'expression': expression,
            'result': result,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_pinned': is_pinned
        }
        self.calculations.insert(0, calculation)  # Insert di awal untuk urutan terbaru
        self.save_history()
    
    def remove_calculation(self, calc_id):
        """Menghapus perhitungan dari history"""
        self.calculations = [calc for calc in self.calculations if calc['id'] != calc_id]
        self.save_history()
    
    def toggle_pin(self, calc_id):
        """Toggle pin status perhitungan"""
        for calc in self.calculations:
            if calc['id'] == calc_id:
                calc['is_pinned'] = not calc['is_pinned']
                break
        self.save_history()
    
    def clear_all_history(self):
        """Menghapus semua history kecuali yang di-pin"""
        self.calculations = [calc for calc in self.calculations if calc['is_pinned']]
        self.save_history()
    
    def get_sorted_calculations(self):
        """Mendapatkan perhitungan yang diurutkan (pinned di atas)"""
        pinned = [calc for calc in self.calculations if calc['is_pinned']]
        unpinned = [calc for calc in self.calculations if not calc['is_pinned']]
        return pinned + unpinned
    
    def save_history(self):
        """Menyimpan history ke file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.calculations, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Memuat history dari file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.calculations = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.calculations = []

class HistoryWindow:
    def __init__(self, parent, history_manager, callback=None):
        self.parent = parent
        self.history_manager = history_manager
        self.callback = callback
        
        # Window untuk history
        self.window = ctk.CTkToplevel(parent)
        self.window.title("History Perhitungan")
        self.window.geometry("500x600")
        self.window.resizable(True, True)
        
        # Pastikan window muncul di depan
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.refresh_history()
    
    def create_widgets(self):
        """Membuat widget untuk window history"""
        # Header frame
        header_frame = ctk.CTkFrame(self.window)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 History Perhitungan",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Clear all button
        self.clear_all_btn = ctk.CTkButton(
            header_frame,
            text="🗑️ Hapus Semua",
            width=100,
            fg_color="#ff4444",
            hover_color="#ff6666",
            command=self.clear_all_history
        )
        self.clear_all_btn.pack(side="right", padx=10, pady=10)
        
        # Scrollable frame untuk history items
        self.scroll_frame = ctk.CTkScrollableFrame(self.window)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def refresh_history(self):
        """Memperbarui tampilan history"""
        # Hapus semua widget yang ada
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        calculations = self.history_manager.get_sorted_calculations()
        
        if not calculations:
            # Tampilkan pesan jika tidak ada history
            no_history_label = ctk.CTkLabel(
                self.scroll_frame,
                text="📝 Belum ada perhitungan tersimpan",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_history_label.pack(pady=50)
            return
        
        # Tampilkan setiap perhitungan
        for calc in calculations:
            self.create_history_item(calc)
    
    def create_history_item(self, calc):
        """Membuat item history individual"""
        # Frame untuk setiap item
        item_frame = ctk.CTkFrame(self.scroll_frame)
        item_frame.pack(fill="x", padx=5, pady=5)
        
        # Background color berbeda untuk item yang di-pin
        if calc['is_pinned']:
            item_frame.configure(fg_color="#2d4a3a")  # Hijau gelap untuk pinned
        
        # Main content frame
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Top row: expression dan pin button
        top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 5))
        
        # Pin indicator dan expression
        expression_text = calc['expression']
        if calc['is_pinned']:
            expression_text = f"📌 {expression_text}"
        
        expression_label = ctk.CTkLabel(
            top_frame,
            text=expression_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        expression_label.pack(side="left", fill="x", expand=True)
        
        # Pin button
        pin_text = "📌" if calc['is_pinned'] else "📍"
        pin_color = "#4a9eff" if calc['is_pinned'] else "#666666"
        
        pin_btn = ctk.CTkButton(
            top_frame,
            text=pin_text,
            width=30,
            height=25,
            fg_color=pin_color,
            command=lambda c=calc: self.toggle_pin(c['id'])
        )
        pin_btn.pack(side="right", padx=(5, 0))
        
        # Middle row: result
        result_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        result_frame.pack(fill="x", pady=(0, 5))
        
        result_label = ctk.CTkLabel(
            result_frame,
            text=f"= {calc['result']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        result_label.pack(side="left", fill="x", expand=True)
        
        # Use button
        use_btn = ctk.CTkButton(
            result_frame,
            text="📋 Gunakan",
            width=80,
            height=25,
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            command=lambda r=calc['result']: self.use_result(r)
        )
        use_btn.pack(side="right", padx=(5, 0))
        
        # Bottom row: timestamp dan delete button
        bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        bottom_frame.pack(fill="x")
        
        timestamp_label = ctk.CTkLabel(
            bottom_frame,
            text=calc['timestamp'],
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        timestamp_label.pack(side="left")
        
        # Delete button (tidak bisa hapus jika di-pin)
        if not calc['is_pinned']:
            delete_btn = ctk.CTkButton(
                bottom_frame,
                text="🗑️",
                width=30,
                height=25,
                fg_color="#ff4444",
                hover_color="#ff6666",
                command=lambda c=calc: self.delete_calculation(c['id'])
            )
            delete_btn.pack(side="right")
    
    def toggle_pin(self, calc_id):
        """Toggle pin status"""
        self.history_manager.toggle_pin(calc_id)
        self.refresh_history()
    
    def delete_calculation(self, calc_id):
        """Hapus perhitungan"""
        if messagebox.askyesno("Konfirmasi", "Hapus perhitungan ini dari history?"):
            self.history_manager.remove_calculation(calc_id)
            self.refresh_history()
    
    def use_result(self, result):
        """Gunakan hasil perhitungan di kalkulator utama"""
        if self.callback:
            self.callback(str(result))
        self.window.destroy()
    
    def clear_all_history(self):
        """Hapus semua history kecuali yang di-pin"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua history kecuali yang di-pin?"):
            self.history_manager.clear_all_history()
            self.refresh_history()

class ScientificCalculator:
    def __init__(self):
        # Konfigurasi tema dan warna
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Inisialisasi window utama
        self.root = ctk.CTk()
        self.root.title("Kalkulator Scientific")
        self.root.geometry("500x700")  # Lebih lebar untuk tab
        self.root.resizable(False, False)
        
        # Variabel untuk menyimpan ekspresi dan hasil
        self.expression = ""
        self.result_var = tk.StringVar()
        self.result_var.set("0")
        
        # History manager
        self.history_manager = CalculationHistory()
        
        # Unit converter
        self.unit_converter = UnitConverter()
        
        # Setup tampilan GUI dengan tabs
        self.create_tabview()
        self.bind_keyboard_events()
        
    def create_tabview(self):
        """Membuat tab view untuk kalkulator dan unit converter"""
        # Main tabview
        self.tabview = ctk.CTkTabview(self.root, width=480, height=680)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab kalkulator
        self.calc_tab = self.tabview.add("🧮 Kalkulator")
        self.create_calculator_widgets()
        
        # Tab unit converter
        self.converter_tab = self.tabview.add("🔄 Unit Converter")
        self.create_converter_widgets()
        
        # Tab financial calculator
        self.financial_tab = self.tabview.add("💹 Financial Calculator")
        self.financial_calculator = FinancialCalculator(self.financial_tab)
        self.financial_calculator.pack(fill="both", expand=True, padx=6, pady=6)
        self.tabview.set("🧮 Kalkulator")
        
        #Tab Geometry & Engineering
        self.geometry_tab = self.tabview.add("📐 Geometry & Engineering")
        self.geometry_calculator = GeometryEngineeringCalculator(self.geometry_tab)
        self.geometry_calculator.pack(fill='both', expand=True, padx=6, pady=6)

        # --- Tambahkan Settings TAB ---
        self.settings_tab = self.tabview.add("⚙️ Settings")
        # INISIALISASI keyboard manager sekali saja!
        self.keyboard_man = KeyboardShortcutManager(self.root, self.show_history)  # pastikan self.show_history sudah ada.
        self.settings_panel = SettingsPanel(self.settings_tab, self.root, self.keyboard_man)
        self.settings_panel.pack(fill="both", expand=True, padx=6, pady=6)

        # Set tab default
        self.tabview.set("🧮 Kalkulator")
        
    def create_calculator_widgets(self):
        """Membuat widget untuk tab kalkulator"""
        # Frame utama untuk kalkulator
        calc_frame = ctk.CTkFrame(self.calc_tab)
        calc_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header frame untuk tombol-tombol utility
        header_frame = ctk.CTkFrame(calc_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # History button
        history_btn = ctk.CTkButton(
            header_frame,
            text="📊 History",
            width=100,
            height=30,
            fg_color="#4a9eff",
            hover_color="#6bb3ff",
            command=self.show_history
        )
        history_btn.pack(side="right")
        
        # Display untuk menampilkan hasil
        self.display = ctk.CTkEntry(
            calc_frame,
            textvariable=self.result_var,
            font=ctk.CTkFont(size=24, weight="bold"),
            height=60,
            justify="right",
            state="readonly"
        )
        self.display.pack(fill="x", padx=10, pady=(10, 20))
        
        # Frame untuk tombol-tombol
        buttons_frame = ctk.CTkFrame(calc_frame)
        buttons_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Definisi tombol dengan baris dan kolom
        self.buttons = [
            # Baris 1: Fungsi matematika lanjutan
            [("sin", 0, 0), ("cos", 0, 1), ("tan", 0, 2), ("log", 0, 3), ("ln", 0, 4)],
            
            # Baris 2: Fungsi tambahan
            [("x²", 1, 0), ("√", 1, 1), ("x!", 1, 2), ("%", 1, 3), ("π", 1, 4)],
            
            # Baris 3: Clear functions
            [("AC", 2, 0), ("C", 2, 1), ("⌫", 2, 2), ("÷", 2, 3), ("×", 2, 4)],
            
            # Baris 4-7: Angka dan operasi dasar
            [("7", 3, 0), ("8", 3, 1), ("9", 3, 2), ("-", 3, 3), ("+", 3, 4)],
            [("4", 4, 0), ("5", 4, 1), ("6", 4, 2), ("(", 4, 3), (")", 4, 4)],
            [("1", 5, 0), ("2", 5, 1), ("3", 5, 2), (".", 5, 3), ("=", 5, 4)],
            [("0", 6, 0, 2)]  # Tombol 0 menggunakan 2 kolom
        ]
        
        # Membuat tombol-tombol
        for row in self.buttons:
            for button_info in row:
                if len(button_info) == 4:  # Tombol dengan colspan
                    text, r, c, colspan = button_info
                    self.create_button(buttons_frame, text, r, c, colspan=colspan)
                else:
                    text, r, c = button_info
                    self.create_button(buttons_frame, text, r, c)
        
        # Konfigurasi grid untuk responsive design
        for i in range(7):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            buttons_frame.grid_columnconfigure(i, weight=1)
    
    def create_converter_widgets(self):
        """Membuat widget untuk tab unit converter"""
        # Main frame
        main_frame = ctk.CTkFrame(self.converter_tab)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔄 Unit Converter",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Category selection
        category_frame = ctk.CTkFrame(main_frame)
        category_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(category_frame, text="Kategori:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.category_var = ctk.StringVar(value="length")
        categories = [
            ("📏 Panjang", "length"),
            ("⚖️ Berat", "weight"),
            ("🌡️ Suhu", "temperature"),
            ("🪣 Volume", "volume"),
            ("💰 Mata Uang", "currency"),
            ("⚡ Energi", "energy")
        ]
        
        # Category buttons
        category_buttons_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        category_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.category_buttons = []
        for i, (text, value) in enumerate(categories):
            btn = ctk.CTkButton(
                category_buttons_frame,
                text=text,
                width=80,
                height=30,
                command=lambda v=value: self.select_category(v)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            self.category_buttons.append((btn, value))
        
        # Configure grid
        for i in range(3):
            category_buttons_frame.grid_columnconfigure(i, weight=1)
        
        # Input section
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Input value
        ctk.CTkLabel(input_frame, text="Nilai:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.input_var = tk.StringVar()
        self.input_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.input_var,
            font=ctk.CTkFont(size=16),
            height=40,
            placeholder_text="Masukkan nilai..."
        )
        self.input_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # From unit
        from_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        from_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(from_frame, text="Dari:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.from_unit_var = ctk.StringVar()
        self.from_unit_menu = ctk.CTkOptionMenu(from_frame, variable=self.from_unit_var)
        self.from_unit_menu.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # To unit
        to_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        to_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(to_frame, text="Ke:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.to_unit_var = ctk.StringVar()
        self.to_unit_menu = ctk.CTkOptionMenu(to_frame, variable=self.to_unit_var)
        self.to_unit_menu.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            main_frame,
            text="🔄 Konversi",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            command=self.perform_conversion
        )
        self.convert_btn.pack(fill="x", padx=10, pady=(0, 20))
        
        # Result section
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(result_frame, text="Hasil:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            height=100,
            font=ctk.CTkFont(size=14),
            state="disabled"
        )
        self.result_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Currency info label (untuk menampilkan info mata uang)
        self.currency_info = ctk.CTkLabel(
            main_frame,
            text="💡 Tip: Untuk mata uang, pastikan koneksi internet aktif",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.currency_info.pack(pady=(0, 10))
        
        # Initialize dengan kategori default
        self.select_category("length")
    
    def select_category(self, category):
        """Memilih kategori konversi"""
        self.category_var.set(category)
        
        # Update button colors
        for btn, value in self.category_buttons:
            if value == category:
                btn.configure(fg_color="#4CAF50")
            else:
                btn.configure(fg_color="#1f538d")  # Default color
        
        # Update unit options
        self.update_unit_options(category)
        
        # Show/hide currency info
        if category == "currency":
            self.currency_info.configure(text="💡 Data kurs real-time - Pastikan koneksi internet aktif")
        else:
            self.currency_info.configure(text="💡 Masukkan nilai dan pilih unit untuk konversi")
    
    def update_unit_options(self, category):
        """Update pilihan unit berdasarkan kategori"""
        units = list(self.unit_converter.conversions[category].keys())
        
        if category == 'currency':
            # Untuk mata uang, tampilkan kode mata uang yang lebih user-friendly
            currency_display = {
                'USD': 'USD - US Dollar',
                'EUR': 'EUR - Euro',
                'JPY': 'JPY - Japanese Yen',
                'GBP': 'GBP - British Pound',
                'AUD': 'AUD - Australian Dollar',
                'CAD': 'CAD - Canadian Dollar',
                'CHF': 'CHF - Swiss Franc',
                'CNY': 'CNY - Chinese Yuan',
                'SEK': 'SEK - Swedish Krona',
                'NZD': 'NZD - New Zealand Dollar',
                'MXN': 'MXN - Mexican Peso',
                'SGD': 'SGD - Singapore Dollar',
                'HKD': 'HKD - Hong Kong Dollar',
                'NOK': 'NOK - Norwegian Krone',
                'IDR': 'IDR - Indonesian Rupiah'
            }
            display_units = [currency_display.get(unit, unit) for unit in units]
        else:
            # Capitalize first letter untuk unit lainnya
            display_units = [unit.capitalize() for unit in units]
        
        # Update option menus
        self.from_unit_menu.configure(values=display_units)
        self.to_unit_menu.configure(values=display_units)
        
        # Set default values
        if display_units:
            self.from_unit_var.set(display_units[0])
            self.to_unit_var.set(display_units[1] if len(display_units) > 1 else display_units[0])
    
    def get_unit_key(self, display_unit, category):
        """Mendapatkan key unit dari display text"""
        if category == 'currency':
            return display_unit.split(' - ')[0]
        else:
            return display_unit.lower()
    
    def perform_conversion(self):
        """Melakukan konversi unit"""
        try:
            # Validasi input
            input_text = self.input_var.get().strip()
            if not input_text:
                self.show_result_error("Masukkan nilai yang akan dikonversi")
                return
            
            try:
                value = float(input_text)
            except ValueError:
                self.show_result_error("Nilai harus berupa angka")
                return
            
            category = self.category_var.get()
            from_unit = self.get_unit_key(self.from_unit_var.get(), category)
            to_unit = self.get_unit_key(self.to_unit_var.get(), category)
            
            if from_unit == to_unit:
                result = value
                self.show_result_success(f"{value} {from_unit} = {result} {to_unit}")
                return
            
            # Show loading untuk mata uang
            if category == 'currency':
                self.show_result_loading("Mengambil data kurs terbaru...")
                self.root.update()
            
            # Perform conversion in separate thread untuk mata uang
            if category == 'currency':
                def convert_currency():
                    try:
                        result = self.unit_converter.convert(value, from_unit, to_unit, category)
                        # Format hasil mata uang
                        formatted_result = f"{value:,.2f} {from_unit} = {result:,.2f} {to_unit}"
                        self.root.after(0, lambda: self.show_result_success(formatted_result))
                    except Exception as e:
                        error_msg = str(e)
                        if "d14ebfc4b79f612afe151532" in error_msg or "api_key" in error_msg.lower():
                            error_msg = "API Key mata uang belum dikonfigurasi. Lihat instruksi di kode."
                        self.root.after(0, lambda: self.show_result_error(f"Error: {error_msg}"))
                
                Thread(target=convert_currency, daemon=True).start()
            else:
                # Konversi langsung untuk unit lainnya
                result = self.unit_converter.convert(value, from_unit, to_unit, category)
                
                # Format hasil
                if category == 'temperature':
                    formatted_result = f"{value}° {from_unit.capitalize()} = {result:.2f}° {to_unit.capitalize()}"
                else:
                    formatted_result = f"{value} {from_unit} = {result:.6f} {to_unit}".rstrip('0').rstrip('.')
                
                self.show_result_success(formatted_result)
                
        except Exception as e:
            self.show_result_error(f"Error: {str(e)}")
    
    def show_result_success(self, message):
        """Menampilkan hasil konversi yang berhasil"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)
        self.result_text.configure(state="disabled", text_color="white")
    
    def show_result_error(self, message):
        """Menampilkan pesan error"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)
        self.result_text.configure(state="disabled", text_color="#ff6b6b")
    
    def show_result_loading(self, message):
        """Menampilkan pesan loading"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)
        self.result_text.configure(state="disabled", text_color="#ffd93d")
    
    def create_button(self, parent, text, row, col, colspan=1):
        """Membuat tombol dengan styling yang konsisten"""
        # Tentukan warna berdasarkan jenis tombol
        if text in ["AC", "C", "⌫"]:
            color = "#ff4444"  # Merah untuk clear
        elif text in ["÷", "×", "-", "+", "="]:
            color = "#ff9500"  # Orange untuk operator
        elif text in ["sin", "cos", "tan", "log", "ln", "x²", "√", "x!", "%", "π"]:
            color = "#666666"  # Abu-abu untuk fungsi scientific
        else:
            color = "#333333"  # Gelap untuk angka
        
        button = ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=color,
            hover_color=self.get_hover_color(color),
            command=lambda t=text: self.button_click(t)
        )
        button.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)
    
    def get_hover_color(self, color):
        """Mendapatkan warna hover yang lebih terang"""
        color_map = {
            "#ff4444": "#ff6666",
            "#ff9500": "#ffad33",
            "#666666": "#888888",
            "#333333": "#555555"
        }
        return color_map.get(color, "#555555")
    
    def show_history(self):
        """Menampilkan window history"""
        HistoryWindow(self.root, self.history_manager, self.use_from_history)
    
    def use_from_history(self, result):
        """Menggunakan hasil dari history"""
        self.expression = result
        self.update_display()
    
    def button_click(self, value):
        """Menangani klik tombol"""
        try:
            if value == "AC":
                self.all_clear()
            elif value == "C":
                self.clear()
            elif value == "⌫":
                self.backspace()
            elif value == "=":
                self.calculate()
            elif value in ["sin", "cos", "tan"]:
                self.add_trig_function(value)
            elif value == "log":
                self.add_function("log10")
            elif value == "ln":
                self.add_function("log")
            elif value == "x²":
                self.add_power()
            elif value == "√":
                self.add_function("sqrt")
            elif value == "x!":
                self.add_factorial()
            elif value == "%":
                self.add_percentage()
            elif value == "π":
                self.add_pi()
            elif value == "÷":
                self.add_operator("/")
            elif value == "×":
                self.add_operator("*")
            else:
                self.add_to_expression(value)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    def add_to_expression(self, value):
        """Menambahkan nilai ke ekspresi"""
        if self.result_var.get() == "0" and value.isdigit():
            self.expression = value
        else:
            self.expression += str(value)
        self.update_display()
    
    def add_operator(self, operator):
        """Menambahkan operator ke ekspresi"""
        if self.expression and self.expression[-1] not in "+-*/":
            self.expression += operator
            self.update_display()
    
    def add_trig_function(self, func):
        """Menambahkan fungsi trigonometri"""
        self.expression += f"math.{func}(math.radians("
        self.update_display()
    
    def add_function(self, func):
        """Menambahkan fungsi matematika"""
        if func == "log10":
            self.expression += "math.log10("
        elif func == "log":
            self.expression += "math.log("
        elif func == "sqrt":
            self.expression += "math.sqrt("
        self.update_display()
    
    def add_power(self):
        """Menambahkan operasi kuadrat"""
        if self.expression:
            # Cari angka terakhir untuk dikuadratkan
            i = len(self.expression) - 1
            while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == '.'):
                i -= 1
            
            if i < len(self.expression) - 1:
                number = self.expression[i+1:]
                self.expression = self.expression[:i+1] + f"({number})**2"
            else:
                self.expression += "**2"
        self.update_display()
    
    def add_factorial(self):
        """Menambahkan operasi faktorial"""
        if self.expression:
            # Cari angka terakhir untuk faktorial
            i = len(self.expression) - 1
            while i >= 0 and self.expression[i].isdigit():
                i -= 1
            
            if i < len(self.expression) - 1:
                number = self.expression[i+1:]
                self.expression = self.expression[:i+1] + f"math.factorial({number})"
            else:
                self.expression = f"math.factorial({self.expression})"
        self.update_display()
    
    def add_percentage(self):
        """Menambahkan operasi persentase"""
        if self.expression:
            self.expression += "/100"
        self.update_display()
    
    def add_pi(self):
        """Menambahkan konstanta pi"""
        self.expression += "math.pi"
        self.update_display()
    
    def calculate(self):
        """Menghitung hasil ekspresi"""
        try:
            if self.expression:
                # Simpan ekspresi asli untuk history
                original_expression = self.expression
                
                # Ganti operator display dengan operator Python
                calc_expression = self.expression.replace("×", "*").replace("÷", "/")
                
                # Evaluasi ekspresi dengan fungsi math yang aman
                result = eval(calc_expression, {"__builtins__": {}, "math": math})
                
                # Format hasil
                if isinstance(result, float):
                    if result.is_integer():
                        result = int(result)
                    else:
                        result = round(result, 10)
                
                # Simpan ke history
                self.history_manager.add_calculation(original_expression, result)
                
                self.result_var.set(str(result))
                self.expression = str(result)
                
        except ZeroDivisionError:
            messagebox.showerror("Error", "Tidak bisa membagi dengan nol!")
            self.all_clear()
        except ValueError as e:
            messagebox.showerror("Error", f"Nilai tidak valid: {str(e)}")
            self.all_clear()
        except Exception as e:
            messagebox.showerror("Error", f"Ekspresi tidak valid: {str(e)}")
            self.all_clear()
    
    def all_clear(self):
        """Menghapus semua (AC)"""
        self.expression = ""
        self.result_var.set("0")
    
    def clear(self):
        """Menghapus input terakhir (C)"""
        self.expression = ""
        self.result_var.set("0")
    
    def backspace(self):
        """Menghapus karakter terakhir"""
        if self.expression:
            self.expression = self.expression[:-1]
            if not self.expression:
                self.result_var.set("0")
            else:
                self.update_display()
    
    def update_display(self):
        """Memperbarui tampilan display"""
        display_text = self.expression if self.expression else "0"
        # Batasi panjang display untuk kerapian
        if len(display_text) > 25:
            display_text = display_text[-25:]
        self.result_var.set(display_text)
    
    def bind_keyboard_events(self):
        """Mengikat event keyboard"""
        self.root.bind('<Key>', self.key_press)
        self.root.focus_set()
    
    def key_press(self, event):
        """Menangani input keyboard"""
        # Only handle keyboard events when calculator tab is active
        if self.tabview.get() != "🧮 Kalkulator":
            return
            
        key = event.char
        
        # Mapping keyboard ke tombol
        key_map = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '+': '+', '-': '-', '*': '×', '/': '÷',
            '.': '.', '(': '(', ')': ')',
            '\r': '=', '\n': '=',  # Enter key
        }
        
        # Special keys
        if event.keysym == 'BackSpace':
            self.button_click('⌫')
        elif event.keysym == 'Delete':
            self.button_click('C')
        elif event.keysym == 'Escape':
            self.button_click('AC')
        elif event.keysym == 'F1':  # F1 untuk buka history
            self.show_history()
        elif key in key_map:
            self.button_click(key_map[key])
    
    def run(self):
        """Menjalankan aplikasi"""
        self.root.mainloop()

# Fungsi utama untuk menjalankan aplikasi
def main():
    """
    Kalkulator Scientific dengan Unit Converter
    
    INSTALASI DEPENDENCIES:
    pip install customtkinter requests
    
    KONFIGURASI API MATA UANG:
    1. Daftar gratis di: https://app.exchangerate-api.com/sign-up/free
    2. Dapatkan API key gratis (1500 request/bulan)
    3. Ganti "YOUR_API_KEY_HERE" di kelas CurrencyConverter dengan API key Anda
    
    FITUR KALKULATOR:
    - Operasi matematika dasar (+, -, ×, ÷)
    - Fungsi scientific (sin, cos, tan, log, ln, √, x², x!)
    - Konstanta π
    - History perhitungan dengan pin/unpin
    - Keyboard shortcuts
    
    FITUR UNIT CONVERTER:
    📏 Panjang: meter, kilometer, feet, inch, mile
    ⚖️ Berat: kilogram, gram, pound, ounce  
    🌡️ Suhu: celsius, fahrenheit, kelvin
    🪣 Volume: liter, gallon, milliliter
    💰 Mata Uang: 15+ mata uang dengan kurs real-time
    ⚡ Energi: joule, calorie, BTU
    
    CARA MENGGUNAKAN:
    1. Jalankan aplikasi: python calculator.py
    2. Tab "🧮 Kalkulator" untuk perhitungan matematika
    3. Tab "🔄 Unit Converter" untuk konversi satuan
    4. Untuk mata uang, pastikan koneksi internet aktif
    
    KEYBOARD SHORTCUTS (tab kalkulator):
    - Angka 0-9: input angka
    - +, -, *, /: operasi matematika
    - Enter: hitung hasil (=)
    - Backspace: hapus karakter terakhir
    - Delete: clear input (C)
    - Escape: clear semua (AC)
    - F1: buka history
    """
    try:
        calculator = ScientificCalculator()
        calculator.run()
    except ImportError as e:
        print("Error: Dependencies tidak terinstall!")
        print("Silakan install dengan perintah:")
        print("pip install customtkinter requests")
        print(f"Detail error: {str(e)}")
    except Exception as e:
        print(f"Error menjalankan aplikasi: {str(e)}")

# Menjalankan aplikasi jika file ini dijalankan langsung
if __name__ == "__main__":
    main()