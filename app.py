import json
import urllib.request
import base64
import ssl
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ALL SYMBOLS
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
    "Volatility 30 (1s) Index": "1HZ30V",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 10 Index": "R_10",
    "Volatility 25 Index": "R_25",
    "Step Index": "stpRNG",
    "DEX 600 UP Index": "DEX600",
    "XAUUSD": "frxXAUUSD",
    "XAUUSDmicro": "frxXAUUSD",
    "Step Index 300": "stpRNG3",
    "Vol over Boom 400": "VOB400",
    "Boom 150 Index": "BOOM150"
}

st.set_page_config(page_title="Quant HFT Institutional Matrix App", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #00ff7f; color: black; font-weight: bold; border-radius: 10px; height: 52px; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Quant HFT Matrix Engine")
st.write("Live Real-Time Market SMC / Wyckoff / 100-Indicator Matrix")

st.sidebar.header("⚙️ Institutional Settings")
gemini_key = st.sidebar.text_input("Gemini API Key:", type="password")

default_prompt = """Act as a Tier-1 Quantitative HFT (High-Frequency Trading) Algorithmic Matrix. I am providing you with a multi-timeframe chart snapshot chain (D1, H4, H1, M15, M5, M1). Your mission is to extract the complete raw mathematical data of 100+ Quantitative Indicators and blend it with every major institutional trading methodology into a single "Institutional Alpha Shake" to generate a definitive, high-probability execution signal.

Analyze the chart assets using the complete suite of the following layers simultaneously:
• if signal provide base on fvg/supply &demand ob than unmitigated Must check.✔️ 

1.--------------
THE INSTITUTIONAL METHODOLOGY SHAKE (SMC, ICT, WYCKOFF & PRICE ACTION):
- ICT & SMC Core: Scan for Break of Structure (BOS), Market Structure Shift / Change of Character (CHoCH), and displacement. Map raw Order Blocks (OB) and institutional Order Flow.
- Liquidity & Sweeps: Identify external/internal Swing Highs and Lows, Equal Highs/Lows (EQH/EQL), and Trendline liquidity. Scan for immediate "Run on Liquidity" (Sweeps) and determine the algorithmic "Draw on Liquidity" (DOL).
- Value Gaps & Zones: Map high-probability Supply and Demand Zones, (unmitigated consider strong Supply& demand) only. 
- Fair Value Gaps (FVG), Inversion FVGs (iFVG), and Balanced Price Ranges (BPR).
- Chart Patterns & Breakouts: Map ascending/descending Trendlines and Parallel Channels. Differentiate between aggressive True Breakouts and institutional Liquidity Hunts/Fakeouts.
- Support & Resistance: Factor in structural Key Levels, Psychological Levels, and Major Pivots.
- Wyckoff Schematic Filter: Scan for Accumulation/Distribution phases, identifying Spring, Upthrust (UT), UTAD, and Last Point of Support/Supply (LPS).

INPUT MARKET DATA:
. Asset: {symbol}
. Current Exact Price: {current_price}
. Recent High: {recent_high}
. Recent Low: {recent_low}

RULES:
1. Valid BUY entries only occur in Phase D/E after a confirmed Spring/Shakeout and Test (LPS) in Accumulation.
2. Valid SELL entries only occur in Phase D/E after a confirmed UTAD and Test (LPSD) in Distribution.
3. If price is in Phase A or B (Consolidation/Building Cause), output "NO TRADE / BUILDING CAUSE".

2.-------------
THE 100-INDICATOR QUANTITATIVE ENGINE (4 SPECIALIZED CLUSTERS):
- Trend & Moving Average Array (30 Indicators)
- Momentum & Exhaustion Oscillators (30 Indicators)
- Volume & Institutional Order Flow (20 Indicators)
- Volatility, Bands & Channels (20 Indicators)

3.-------------
REQUIRED OUTPUT FORMAT:
1. Executive Summary: Short overall assessment of technical alignment.
2. Indicator Consensus: Percentage of indicators bullish vs. bearish.
3. Conflict Analysis: List any indicators giving opposite/conflicting signals.
4. Trade Verdict: [STRONG BUY / BUY / NO TRADE / SELL / STRONG SELL]
5. Overall Confidence Rating: [1/10 to 10/10]

4.--------------
Integrated Indicator Stack & Logic Breakdown:
* Trend & Dynamic Filtering: NSDT HAMA Candles, UT Bot Alerts.
* Smart Money Concepts & Liquidity: SMC Target Liquidity V.35, Supply and Demand, Order Blocks Rejection Trader.
* Fair Value Gaps & Imbalances: LuxAlgo - FVG Positioning, FVG/iFVG (Nephew_Sam_).
* Geometric & Structural Channels: TriSAD, Zig Zag Channels [LuxAlgo].

5.-------------
THE SWEET-SPOT STOP LOSS ENGINE:
- Place the SL exactly 1-2 pips/points (or a structural safety margin based on ATR and lower timeframe wicks) below/above the true unmitigated structural discount driver. This filters broker spreads and retail hunts while maintaining an optimal Risk-to-Reward (R:R) ratio between 1:2 and 1:4.

6.----------
FINAL SIGNAL EXECUTION FORMAT:
🔔 SMT
📊 Asset: {symbol}
⏱️ Timeframe: M15
📈/📉 Signal: [Buy / Sell / No Trade]
🎯 TP: [Target Level / 🔥🔥 ]
⚪ SL: [Stop Loss]
💡 Logic: [Detailed SMC / Indicator Breakdown]"""

custom_prompt = st.sidebar.text_area("Custom AI Logic / Institutional Prompt:", value=default_prompt, height=450)

symbol = st.selectbox("Select Asset / Pair:", list(SYMBOL_MAP.keys()))

def fetch_deriv_rest_candles(symbol_code):
    # Using Deriv public API endpoint via HTTP GET / POST request (Bypasses WS Cloud blocks)
    url = f"https://green.derivws.com/websockets/v3?app_id=1089" # or use public REST endpoint if available, but let's use public public JSON API via urllib POST
    # Deriv also supports public HTTP endpoint via web interface or standard public API gateway
    api_endpoint = "https://base.deriv.com/api/v3/ticks_history" # fallback public api
    
    # Alternative: Public Deriv App ID query via standard urllib with standard JSON-RPC over HTTPS if supported, 
    # Let's use Deriv public public HTTP proxy or standard public server API:
    try:
        # We can query standard public endpoint or public WebSocket via alternative pool
        import websocket
        ws_urls = [
            "wss://green.derivws.com/websockets/v3?app_id=1089",
            "wss://blue.derivws.com/websockets/v3?app_id=1089",
            "wss://red.derivws.com/websockets/v3?app_id=1089"
        ]
        headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://deriv.com"}
        for u in ws_urls:
            try:
                ws = websocket.create_connection(u, timeout=8, header=headers, sslopt={"cert_reqs": ssl.CERT_NONE})
                payload = {
                    "ticks_history": symbol_code,
                    "adjust_start_time": 1,
                    "count": 40,
                    "end": "latest",
                    "style": "candles",
                    "granularity": 900
                }
                ws.send(json.dumps(payload))
                res = json.loads(ws.recv())
                ws.close()
                if "candles" in res:
                    return "SUCCESS", res["candles"]
                elif "error" in res:
                    return "ERROR", res["error"]["message"]
            except:
                continue
        return "FAIL", "All green/blue/red proxy nodes blocked."
    except Exception as e:
        return "FAIL", str(e)

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
            with urllib.request.urlopen(req, context=context, timeout=20) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                return res_data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            continue

    return "⚠️ AI Analysis response failed. Please retry."

if st.button("⚡ GENERATE SIGNAL NOW"):
    if not gemini_key:
        st.error("⚠️ Pehle Sidebar mein Gemini API Key darj karein!")
    else:
        with st.spinner("⏳ Connecting to Deriv Multi-Region Gateway..."):
            deriv_symbol = SYMBOL_MAP[symbol]
            status, result = fetch_deriv_rest_candles(deriv_symbol)
            
            if status == "ERROR":
                st.error(f"❌ DERIV SERVER ERROR: {result}")
            elif status == "FAIL" or result is None:
                st.error("❌ CLOUD NETWORK NOTICE: Streamlit server IP se Deriv WebSocket restricted hai. Kripya apna local PC par app run karein (`streamlit run app.py`) ya synthetic index select karein.")
            else:
                candles = result
                live_price = candles[-1]['close']
                st.success(f"🟢 Real Market Data Fetched! Current Price: {live_price}")
                
                with st.spinner("⏳ Running 100-Indicator Institutional Matrix Engine..."):
                    chart_path = draw_candlestick_chart(candles)
                    signal_res = get_ai_signal(chart_path, candles, symbol, gemini_key, custom_prompt)
                    
                    st.image(chart_path, caption=f"M15 Real Live Chart ({symbol}) - Exact Price: {live_price}", use_container_width=True)
                    st.markdown("### 🔔 HFT Quantitative Matrix Output")
                    st.info(signal_res)
