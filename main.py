import yfinance as yf
import pandas as pd
import numpy as np
from colorama import init, Fore, Style

# Terminalde renkli çıktıların otomatik olarak sıfırlanması için colorama'yı başlat
init(autoreset=True)


def get_stock_data(ticker, period="1mo"):
    """
    Belirtilen hisse senedi için geçmiş verileri çeker.
    Hata durumunda None döner.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        if data.empty:
            print(Fore.YELLOW + f"Uyarı: {ticker} için veri bulunamadı.")
            return None
        return data
    except Exception as e:
        print(Fore.RED + f"Hata: {ticker} verisi çekilemedi. Sebep: {e}")
        return None


def is_in_uptrend(df, window=20):
    """
    Verilen DataFrame'deki kapanış fiyatlarının son 'window' gün içinde
    yükseliş trendinde olup olmadığını kontrol eder.
    Basit lineer regresyon eğimine bakar.
    """
    if df is None or len(df) < window:
        return False

    # Son 'window' günlük kapanış fiyatlarını al
    recent_closes = df['Close'].tail(window)
    
    # Zaman serisi için x ekseni (0, 1, 2, ...)
    x = np.arange(len(recent_closes))
    
    # Lineer regresyonun eğimini (slope) hesapla
    slope, _ = np.polyfit(x, recent_closes, 1)
    
    # Eğim pozitifse yükseliş trendindedir
    return slope > 0


def calculate_momentum_score(df, window=14):
    """
    Göreceli Güç Endeksi'ni (RSI) hesaplayarak 0-100 arası bir momentum puanı verir.
    """
    if df is None or len(df) < window:
        return 0

    # Fiyat değişimlerini hesapla
    delta = df['Close'].diff()

    # Kazançları ve kayıpları ayır
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # Göreceli Güç (RS)
    rs = gain / loss
    
    # RSI
    rsi = 100 - (100 / (1 + rs))
    
    # Son RSI değerini puan olarak al, NaN ise 0 dön
    last_rsi = rsi.iloc[-1]
    
    return last_rsi if not np.isnan(last_rsi) else 0


def get_news_sentiment(ticker):
    """
    Hisse senedi ile ilgili haberlerin duygu analizini yapar.
    NOT: Bu fonksiyon şu anda bir yer tutucudur ve her zaman 'Pozitif' döner.
    Gerçek bir NLTK entegrasyonu gerektirir.
    """
    # NLTK kütüphanesinin indirilmesi ve kurulumu karmaşık olabileceğinden
    # bu adımda basit bir yer tutucu kullanıyoruz.
    return "Pozitif"


def get_portfolio_suggestion(momentum_score):
    """
    Momentum puanına göre portföy yatırım önerisi yüzdesi ve kar hedefi yüzdesi oluşturur.
    """
    if momentum_score > 70:
        # Güçlü momentum: Daha yüksek risk, daha yüksek potansiyel
        allocation_percentage = 5.0
        profit_target_percentage = 15.0
    elif momentum_score > 50:
        # Orta momentum: Dengeli yaklaşım
        allocation_percentage = 3.0
        profit_target_percentage = 10.0
    else:
        # Düşük momentum: Düşük sinyal, daha temkinli (genellikle filtrelenir)
        allocation_percentage = 1.5
        profit_target_percentage = 7.0
    
    return allocation_percentage, profit_target_percentage


def run_backtest():
    """
    Stratejinin geçmiş veriler üzerinde test edilmesi için yer tutucu.
    Bu fonksiyon gelecekteki geliştirmeler için tasarlanmıştır.
    """
    print(Fore.CYAN + "\n--- Backtest Modülü ---")
    print(Fore.CYAN + "Bu özellik yakında gelecek. Stratejinin geçmiş performansı burada test edilecek.")
    pass


def avci_modu(tickers, scan_limit=350):
    """
    Ana tarama motoru. Belirlenen hisse listesini tarar ve sinyalleri üretir.
    """
    print(Fore.MAGENTA + Style.BRIGHT + "💸 SAZLIK PRO V40.0 - AVCI MODU BAŞLATILDI 💸")
    print(Fore.MAGENTA + "--------------------------------------------------")
    
    potential_signals = 0
    for i, ticker in enumerate(tickers[:scan_limit]):
        print(f"\n{i+1}/{len(tickers[:scan_limit])} Taranıyor: {ticker}...")
        
        # 1. Veri Çekme
        data = get_stock_data(ticker)
        if data is None:
            continue

        # 2. Trend Filtresi
        if not is_in_uptrend(data):
            print(f"Hisse: {Fore.CYAN}{ticker}{Style.RESET_ALL} | Durum: {Fore.YELLOW}PAS GEÇ (Düşüş Trendi)")
            continue
            
        # 3. Momentum Puanı
        momentum_score = calculate_momentum_score(data)
        momentum_strength = "Güçlü" if momentum_score > 50 else "Zayıf"
        
        # 4. Haber Analizi
        news_sentiment = get_news_sentiment(ticker)
        
        # 5. Karar Mekanizması
        if momentum_score > 50 and news_sentiment == "Pozitif":
            status = Fore.GREEN + "AL"
            potential_signals += 1
            
            # 6. Portföy Önerisi
            allocation, profit_target = get_portfolio_suggestion(momentum_score)
            
            # Çıktı Formatı
            print(f"Hisse: {Fore.CYAN}{ticker}{Style.RESET_ALL} | Puan: {Fore.GREEN}{momentum_score:.2f}")
            print(f"Durum: {status}")
            print(f"Detay: Momentum [{momentum_strength}], Haberler [{news_sentiment}]")
            print(Fore.GREEN + f"Öneri: Kasanın %{allocation}'i ile giriş yap, Hedef Kar: %{profit_target}")

        else:
            status = Fore.YELLOW + "PAS GEÇ"
            print(f"Hisse: {Fore.CYAN}{ticker}{Style.RESET_ALL} | Puan: {Fore.YELLOW}{momentum_score:.2f}")
            print(f"Durum: {status}")
            print(f"Detay: Momentum [{momentum_strength}], Haberler [{news_sentiment}]")

    print(Fore.MAGENTA + "\n--------------------------------------------------")
    print(Fore.MAGENTA + Style.BRIGHT + f"💸 TARAMA TAMAMLANDI! Bulunan potansiyel sinyal sayısı: {potential_signals}")


if __name__ == "__main__":
    # Taranacak hisse senetleri listesi (Nasdaq 100'den popüler hisseler)
    # Gerçek bir tarama için bu liste çok daha uzun olmalıdır (örn. 350+).
    nasdaq_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'ASML', 'AVGO', 
        'PEP', 'COST', 'ADBE', 'CSCO', 'TMUS', 'AMD', 'INTC', 'QCOM', 'TXN', 'AMAT'
    ]
    
    # Avcı Modu'nu başlat
    avci_modu(nasdaq_tickers)
    
    # Backtest modülünü çalıştır (yer tutucu)
    run_backtest()
