import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Force pandas to print all rows instead of truncating the middle
pd.set_option('display.max_rows', None)

# Dictionary mapping the fixed Yahoo Finance tickers to the Company Name
ftse_100_dict = {
    "III.L": "3i Group", "ABDN.L": "abrdn", "ADM.L": "Admiral Group", "AAF.L": "Airtel Africa",
    "ALW.L": "Alliance Witan", "AAL.L": "Anglo American", "ANTO.L": "Antofagasta", "ABF.L": "Associated British Foods",
    "AZN.L": "AstraZeneca", "AUTO.L": "Auto Trader Group", "AV.L": "Aviva", "BAB.L": "Babcock International",
    "BA.L": "BAE Systems", "BBY.L": "Balfour Beatty", "BARC.L": "Barclays", "BTRW.L": "Barratt Redrow",
    "BP.L": "BP", "BATS.L": "British American Tobacco", "BLND.L": "British Land", "BT-A.L": "BT Group",
    "BNZL.L": "Bunzl", "BRBY.L": "Burberry", "CNA.L": "Centrica", "CCEP.L": "Coca-Cola Europacific",
    "CCH.L": "Coca-Cola HBC", "CPG.L": "Compass Group", "CCC.L": "Computacenter", "CTEC.L": "ConvaTec Group",
    "CRDA.L": "Croda International", "DCC.L": "DCC plc", "DGE.L": "Diageo", "DPLM.L": "Diploma",
    "EZJ.L": "easyJet", "EDV.L": "Endeavour Mining", "EXPN.L": "Experian", "FCIT.L": "F&C Investment Trust",
    "FRES.L": "Fresnillo", "GAW.L": "Games Workshop", "GLEN.L": "Glencore", "GSK.L": "GSK",
    "HLN.L": "Haleon", "HLMA.L": "Halma", "HSX.L": "Hiscox", "HWDN.L": "Howden Joinery",
    "HSBA.L": "HSBC", "ICG.L": "Intermediate Capital Group", "IGG.L": "IG Group", "IMI.L": "IMI plc",
    "IMB.L": "Imperial Brands", "INF.L": "Informa", "IHG.L": "InterContinental Hotels",
    "IAG.L": "International Airlines Group",
    "ITRK.L": "Intertek", "INVP.L": "Investec", "ITH.L": "Ithaca Energy", "JD.L": "JD Sports",
    "KGF.L": "Kingfisher", "LAND.L": "Landsec", "LGEN.L": "Legal & General", "BGEO.L": "Lion Finance Group",
    "LLOY.L": "Lloyds Banking Group", "LSEG.L": "London Stock Exchange", "LMP.L": "LondonMetric Property",
    "MNG.L": "M&G",
    "MKS.L": "Marks & Spencer", "MRO.L": "Melrose Industries", "MTLN.L": "Metlen Energy", "NG.L": "National Grid",
    "NWG.L": "NatWest Group", "NXT.L": "Next plc", "PSON.L": "Pearson", "PSH.L": "Pershing Square Holdings",
    "PRU.L": "Prudential", "RKT.L": "Reckitt", "REL.L": "RELX", "RTO.L": "Rentokil Initial",
    "RMV.L": "Rightmove", "RIO.L": "Rio Tinto", "RR.L": "Rolls-Royce", "SGE.L": "Sage Group",
    "SBRY.L": "Sainsbury's", "SGRO.L": "Segro", "SVT.L": "Severn Trent", "SHEL.L": "Shell",
    "SMIN.L": "Smiths Group", "SN.L": "Smith & Nephew", "SPX.L": "Spirax Group", "SSE.L": "SSE plc",
    "STAN.L": "Standard Chartered", "TW.L": "Taylor Wimpey", "TSCO.L": "Tesco", "ULVR.L": "Unilever",
    "UTG.L": "Unite Group", "UU.L": "United Utilities", "VOD.L": "Vodafone", "WEIR.L": "Weir Group",
    "WTB.L": "Whitbread", "WPP.L": "WPP plc", "SMT.L": "Scottish Mortgage", "ENT.L": "Entain",
    "BME.L": "B&M European Value", "FRAS.L": "Frasers Group", "BKG.L": "Berkeley Group", "SDLF.L": "Standard Life",
    "VTY.L": "Vistry Group"
}

ftse_100_tickers = list(ftse_100_dict.keys())


def fetch_and_analyze(tickers):
    print(f"\n{'=' * 60}")
    print(f"MARKET UPDATE: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'=' * 60}")

    try:
        data = yf.download(tickers, period="2d", group_by='ticker', progress=False)

        results = []
        failed_tickers = []

        for ticker in tickers:
            company_name = ftse_100_dict.get(ticker, "Unknown")

            # Check if data exists and clean out Yahoo's NaN (missing) values
            if ticker in data and not data[ticker].empty:
                closes = data[ticker]['Close'].dropna()

                # We need exactly 2 valid closing prices to calculate the % change
                if len(closes) >= 2:
                    prev_close = float(closes.iloc[0])
                    current_price = float(closes.iloc[-1])

                    pct_change = ((current_price - prev_close) / prev_close) * 100

                    results.append({
                        "Ticker": ticker.replace('.L', ''),
                        "Name": company_name,
                        "Price (GBP)": round(current_price, 2),
                        "% Change": round(pct_change, 2)
                    })
                else:
                    failed_tickers.append(company_name)
            else:
                failed_tickers.append(company_name)

        df = pd.DataFrame(results)

        if not df.empty:
            df_sorted = df.sort_values(by='% Change', ascending=False).reset_index(drop=True)
            flags = df_sorted[df_sorted['% Change'] >= 10.0]

            if not flags.empty:
                print("🚨 ALERT: STOCKS UP 10%+ 🚨")
                print(flags.to_string(index=False))
                print("-" * 60)

            print("Full FTSE 100 List (Ranked by % Change):")
            print(df_sorted.to_string(index=False))
            print("-" * 60)

        # Neatly report which stocks Yahoo Finance dropped this minute
        if failed_tickers:
            print(f"⚠️ Yahoo Finance API failed to return data for {len(failed_tickers)} stocks this pass:")
            print(", ".join(failed_tickers))

    except Exception as e:
        print(f"Error fetching data: {e}")


# Continuous tracking loop
while True:
    fetch_and_analyze(ftse_100_tickers)
    print("\nWaiting 60 seconds before next refresh...")
    time.sleep(60)