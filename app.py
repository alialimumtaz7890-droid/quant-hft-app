import json
import urllib.request
import base64
import ssl
import time
from PIL import Image, ImageDraw, ImageFont
import websocket
import streamlit as st

# REAL ACCURATE DERIV SYMBOL MAPPINGS
SYMBOL_MAP = {
    "Boom 1000 Index": "BOOM1000",
    "Crash 1000 Index": "CRASH1000",
    "Crash 500 Index": "CRASH500",
    "Boom 900 Index": "BOOM900",
    "Boom 600 Index": "BOOM600",
    "Crash 600 Index": "CRASH600",
    "Boom 500 Index": "BOOM500",
    "Crash 300 Index": "CRASH300",
    "Boom 300 Index": "BOOM300",
    "Crash 150 Index": "CRASH150",
    "Step Index 500": "stpRNG",
    "Jump 25 Index": "JD25",
    "Volatility 75 Index": "R_75",
    "Volatility 10 Index": "R_10",
    "Volatility 25 Index": "R_25",
    "XAUUSD": "frxXAUUSD"
}

st.set_page_config(page_title="Quant HFT Institutional Matrix App", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #00ff7f; color: black; font-weight: bold; border-radius: 10px; height: 52px; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Quant HFT Matrix Engine")
st.write("Real-Time Deriv Market SMC / Wyckoff / 100-Indicator Matrix")

st.sidebar.header("⚙️ Institutional Settings")
gemini_key = st.sidebar.text_input("Gemini API Key:", type="password")

default_prompt = """Act as a Tier-1 Quantitative HFT Algorithmic Matrix powered by SMC/ICT, Wyckoff Schematics, and 100-Indicator Quantitative Engine.

Analyze this REAL M15 market chart snapshot for symbol: {symbol}.

⚡ REAL-TIME MARKET METRICS (FROM DERIV API):
- Current Live Price: {current_price}
- Recent High: {recent_high}
- Recent Low: {recent_low}

CRITICAL EXECUTION & FILTER RULES:
1. UNMITIGATED ZONES ONLY: Check for unmitigated Supply & Demand zones, unmitigated Order Blocks (OB), Fair Value Gaps (FVG), and Inversion FVGs (iFVG). Mitigated zones MUST be rejected.
2. WYCKOFF PHASE FILTER:
   - BUY entries ONLY in Phase D/E after confirmed Spring/Shakeout & LPS test.
   - SELL entries ONLY in Phase D/E after confirmed UTAD & LPSD test.
   - Phase A/B must output "NO TRADE / BUILDING CAUSE".
3. SWEET-SPOT STOP LOSS ENGINE: Place SL 1-2 pips/points beyond the unmitigated structural invalidation boundary (e.g. sweep wick / active OB base) to filter broker spread and liquidity hunts while maintaining 1:2 to 1:4 R:R.

PROVIDE OUTPUT IN THIS EXACT STRUCTURE:

1. THE INSTITUTIONAL METHODOLOGY SHAKE (SMC, ICT, WYCKOFF & PRICE ACTION)
- ICT/SMC Core: BOS, CHoCH, Displacement, Unmitigated OB/FVG/iFVG mapping.
- Liquidity & Sweeps: Internal/External sweeps, Draw on Liquidity (DOL).
- Wyckoff Phase: Phase A-E status, Spring/UTAD verification.

2. 100-INDICATOR QUANTITATIVE ENGINE & INDICATOR STACK
- Trend Cluster: EMA/SMA Ribbon, HAMA Candles, Cloud, SuperTrend, UT Bot alerts.
- Momentum Cluster: RSI divergence, Stochastic cross, MACD displacement.
- Volume & Volatility Cluster: VWAP, CMF, OBV, ATR.
- Indicator Consensus: % Bullish vs % Bearish.

3. ENTRY STRENGTH & CONFIDENCE SCORE
- Indicator Alignment Fraction (e.g. 88/100 Aligned)
- Entry Strength Score: (0% to 100%)
- Overall Confidence Rating: (1/10 to 10/10)

4. FINAL INSTITUTIONAL SIGNAL EXECUTION FORMAT:
🔔 SMT
📊 Asset: {symbol}
⏱️ Timeframe: M15
📈/📉 Signal: [BUY / SELL / NO TRADE]
🎯 TP1: [Target 1 Price]
🎯 TP2: [Target 2 Price 🔥🔥]
⚪ SL: [Sweet-Spot SL Price]
💡 Entry Logic & Reasons: [Detailed SMC/Wyckoff/Unmitigated OB reason]"""

custom_prompt = st.sidebar.text_area("Custom AI Logic / Institutional Prompt:", value=default_prompt, height=260)

symbol = st.selectbox("Select Asset / Pair:", list(SYMBOL_MAP.keys()))

def fetch_real_deriv_candles(symbol_code):
    ws_url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    try:
        ws = websocket.create_connection(ws_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE})
        payload = {
            "ticks_history": symbol_code,
            "adjust_start_time": 1,
            "count": 40,
            "end": "latest",
            "style": "candles",
            "granularity": 900
        }
        ws.send(json.dumps(payload))
        for _ in range(8):
            res = json.loads(ws.recv())
            if "candles" in res and len(res["candles"]) > 0:
                ws.close()
                return res["candles"]
        ws.close()
    except Exception as e:
        pass
    return None

def draw_candlestick_chart(candles):
    width, height = 750, 400
    img = Image.new("RGB", (width, height), "#0d1117")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
        
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]
    min_p, max_p = min(lows), max(highs)
    p_range = max_p - min_p if max_p != min_p else 1.0
    
    padding_x, padding_y = 65, 45
    chart_h = height - (padding_y * 2)
    n = len(candles)
    slot_w = (width - (padding_x * 2)) / n
    candle_w = max(slot_w * 0.6, 2)
    
    def to_y(price):
        return height - padding_y - int(((price - min_p) / p_range) * chart_h)

    for i in range(5):
        y = padding_y + i * (chart_h / 4)
        price_level = max_p - (i * (p_range / 4))
        draw.line([(padding_x, y), (width - padding_x, y)], fill="#21262d", width=1)
        if font:
            draw.text((5, y - 6), f"{price_level:.2f}", fill="#8b949e", font=font)

    for i, c in enumerate(candles):
        x_center = padding_x + i * slot_w + (slot_w / 2)
        open_y, close_y = to_y(c['open']), to_y(c['close'])
        high_y, low_y = to_y(c['high']), to_y(c['low'])
        color = "#00ff7f" if c['close'] >= c['open'] else "#ff4500"
        
        draw.line([(x_center, high_y), (x_center, low_y)], fill=color, width=1)
        y1, y2 = min(open_y, close_y), max(open_y, close_y)
        draw.rectangle([x_center - (candle_w/2), y1, x_center + (candle_w/2), y2 if y1!=y2 else y2+1], fill=color, outline=color)
    
    img_path = "chart.png"
    img.save(img_path)
    return img_path

def get_ai_signal(img_path, candles, asset_name, api_key, prompt_template):
    with open(img_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode('utf-8')
    
    curr_p = candles[-1]['close']
    r_high = max([c['high'] for c in candles[-10:]])
    r_low = min([c['low'] for c in candles[-10:]])

    formatted_prompt = prompt_template.format(
        current_price=curr_p,
        recent_high=r_high,
        recent_low=r_low,
        symbol=asset_name
    )

    models_to_try = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-1.5-pro"]
    context = ssl._create_unverified_context()

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": formatted_prompt},
                    {"inline_data": {"mime_type": "image/png", "data": b64_img}}
                ]
            }]
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, context=context, timeout=15) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                return res_data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            continue

    return "⚠️ AI Analysis response fail ho gaya. Retry karein."

if st.button("⚡ GENERATE SIGNAL NOW"):
    if not gemini_key:
        st.error("⚠️ Pehle Sidebar mein Gemini API Key darj karein!")
    else:
        with st.spinner("⏳ Fetching REAL Deriv Live Market Data..."):
            deriv_symbol = SYMBOL_MAP[symbol]
            candles = fetch_real_deriv_candles(deriv_symbol)
            
            if not candles:
                st.error(f"❌ Real market data connection fail ho gaya. Koshish karein dobara button dabayein.")
            else:
                live_price = candles[-1]['close']
                st.success(f"✅ Real Live Price Fetched: **{live_price}**")
                
                chart_path = draw_candlestick_chart(candles)
                
                signal_res = get_ai_signal(chart_path, candles, symbol, gemini_key, custom_prompt)
                
                st.image(chart_path, caption=f"M15 Real Live Chart ({symbol}) - Current Price: {live_price}", use_container_width=True)
                st.markdown("### 🔔 HFT Quantitative Matrix Output")
                st.info(signal_res)
