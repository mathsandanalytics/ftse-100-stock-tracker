"""
FTSE 100 Desktop Tracker (GUI Version)
--------------------------------------
This converts the terminal script into a graphical interface using Python's
built-in 'tkinter' library.

It uses a background thread to fetch data so the user interface never freezes,
and applies custom color tags (green, red, and gold) to instantly highlight market movers.
"""

import yfinance as yf
import pandas as pd
import time
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# 1. SETUP & CONFIGURATION
# -------------------------------------------------------------------------
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


# 2. GUI APPLICATION CLASS
# -------------------------------------------------------------------------
class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FTSE 100 Live Tracker")
        self.root.geometry("800x600")

        # Make the table look modern instead of like a Windows 95 app
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        style.configure("Treeview", font=('Arial', 11), rowheight=30)

        # Top banner for status messages
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill=tk.X)
        self.status_label = tk.Label(top_frame, text="Initializing...", font=("Arial", 12, "bold"))
        self.status_label.pack()

        # Create the Table (Treeview)
        columns = ("Ticker", "Name", "Price", "Change")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")

        # Assign Table Headers
        self.tree.heading("Ticker", text="Ticker")
        self.tree.heading("Name", text="Company Name")
        self.tree.heading("Price", text="Price (GBP)")
        self.tree.heading("Change", text="% Change")

        # Set Column Widths and Alignments
        self.tree.column("Ticker", width=100, anchor=tk.CENTER)
        self.tree.column("Name", width=350, anchor=tk.W)
        self.tree.column("Price", width=150, anchor=tk.E)
        self.tree.column("Change", width=150, anchor=tk.E)

        # Define Color Tags for Row Coloring
        self.tree.tag_configure("up", foreground="green")
        self.tree.tag_configure("down", foreground="red")
        self.tree.tag_configure("massive_up", foreground="black", background="gold")
        self.tree.tag_configure("massive_down", foreground="white", background="darkred")

        # Add a Scrollbar
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Start Background Thread
        # Setting daemon=True ensures the background loop dies when you close the window
        self.update_thread = threading.Thread(target=self.fetch_data_loop, daemon=True)
        self.update_thread.start()

    # Thread-safe function to update the top label
    def update_status_ui(self, message):
        self.status_label.config(text=message)

    # Thread-safe function to populate the GUI table
    def populate_table_ui(self, df):
        # Clear out the old rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert the newly calculated rows
        for _, row in df.iterrows():
            pct = row['% Change']

            # Decide which color tag to apply
            if pct >= 10.0:
                tag = "massive_up"
            elif pct <= -10.0:
                tag = "massive_down"
            elif pct > 0:
                tag = "up"
            elif pct < 0:
                tag = "down"
            else:
                tag = ""

            # Insert into the table (formatted nicely)
            self.tree.insert("", tk.END, values=(
                row['Ticker'],
                row['Name'],
                f"£{row['Price (GBP)']:.2f}",
                f"{pct:+.2f}%"  # The + forces positive numbers to show a + sign
            ), tags=(tag,))

    # The infinite loop that lives in the background thread
    def fetch_data_loop(self):
        while True:
            # Tell the main GUI thread to update the status text
            self.root.after(0, self.update_status_ui, "Fetching live market data...")

            try:
                data = yf.download(ftse_100_tickers, period="2d", group_by='ticker', progress=False)
                results = []

                for ticker in ftse_100_tickers:
                    company_name = ftse_100_dict.get(ticker, "Unknown")

                    if ticker in data and not data[ticker].empty:
                        closes = data[ticker]['Close'].dropna()

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

                df = pd.DataFrame(results)
                if not df.empty:
                    # Sort highest to lowest
                    df_sorted = df.sort_values(by='% Change', ascending=False).reset_index(drop=True)

                    # Push the fresh data over to the main GUI thread
                    self.root.after(0, self.populate_table_ui, df_sorted)

                update_time = datetime.now().strftime('%H:%M:%S')
                self.root.after(0, self.update_status_ui, f"Market Data Current as of {update_time} (Auto-refreshing)")

            except Exception as e:
                self.root.after(0, self.update_status_ui, f"Error fetching data: {e}")

            # Sleep the background thread for 60 seconds
            time.sleep(60)


# 3. MAIN EXECUTION
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Boot up the graphical window
    root = tk.Tk()
    app = StockTrackerApp(root)
    # This keeps the window open on your screen
    root.mainloop()