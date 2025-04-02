from flask import Flask, render_template_string, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load CSV File
df = pd.read_csv("TSLA.csv")
df["Date"] = pd.to_datetime(df["Date"])  # Convert Date to datetime

# HTML & JavaScript Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📈 Tesla Stock Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #121212; color: white; }
        h1 { color: #ffcc00; }
        #form-container { margin: 20px auto; padding: 20px; background: #222; width: 50%; border-radius: 10px; box-shadow: 0px 0px 10px rgba(255,255,255,0.1); }
        input { padding: 10px; width: 200px; font-size: 16px; margin-right: 10px; border-radius: 5px; border: none; }
        button { padding: 10px; background-color: #ffcc00; color: black; border: none; cursor: pointer; border-radius: 5px; }
        button:hover { background-color: #ff9900; }
        table { width: 90%; margin: 20px auto; border-collapse: collapse; background: #222; border-radius: 10px; }
        th, td { border: 1px solid #555; padding: 8px; text-align: center; }
        th { background-color: #ffcc00; color: black; }
        #footer { 
            margin-top: 30px; padding: 15px; background-color: #222; color: white; 
            font-size: 16px; border-radius: 10px; position: relative;
        }
        #footer p { margin: 5px 0; }
        #footer a { color: #ff9900; text-decoration: none; font-weight: bold; }
        #footer a:hover { color: white; }
        .footer-animation { animation: fadeIn 2s infinite alternate; color: #ffcc00; }
        @keyframes fadeIn { 0% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <h1>📊 Tesla Stock Data Dashboard</h1>
    <div id="form-container">
        <label>Enter Year: 📅 </label>
        <input type="number" id="year-input" placeholder="YYYY">
        <button onclick="fetchData()">🔎 Fetch Data</button>
    </div>
    <div id="table-container"></div>
    
    <div id="chart-container">
        <div id="stock-chart"></div>
        <div id="volume-chart"></div>
        <div id="candlestick-chart"></div>
    </div>

    <div id="footer">
        <p class="footer-animation">🚀 Made with ❤️ by <strong>Piyush Kumar</strong></p>
        <p>🌐 Connect with me on <a href="https://www.linkedin.com/in/piyush-kumar62/" target="_blank">LinkedIn</a></p>
        <p>📅 <span id="year"></span> | &copy; All Rights Reserved</p>
    </div>

    <script>
        document.getElementById("year").innerText = new Date().getFullYear();

        function fetchData() {
            let year = document.getElementById("year-input").value;
            if (!year) {
                alert("⚠️ Please enter a valid year!");
                return;
            }

            fetch('/get_data?year=' + year)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        displayTable(data);
                        plotChart(data);
                        plotVolumeChart(data);
                        plotCandlestickChart(data);
                    }
                })
                .catch(error => console.log("Error fetching data:", error));
        }

        function displayTable(data) {
            let tableHTML = "<h2>📆 Stock Data for " + data.year + "</h2>";
            tableHTML += "<table><tr><th>#</th><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th><th>Change</th><th>% Change</th><th>Trend</th></tr>";
            for (let i = 0; i < data.date.length; i++) {
                tableHTML += `<tr>
                    <td>${i + 1}</td>
                    <td>${data.date[i]}</td>
                    <td>${data.open[i]}</td>
                    <td>${data.high[i]}</td>
                    <td>${data.low[i]}</td>
                    <td>${data.close[i]}</td>
                    <td>${data.volume[i]}</td>
                    <td>${data.price_diff[i]}</td>
                    <td>${data.percent_change[i].toFixed(2)}%</td>
                    <td style="color:${data.trend[i] == 'Bullish' ? 'lime' : 'red'};">${data.trend[i] == 'Bullish' ? '🚀 Bullish' : '📉 Bearish'}</td>
                </tr>`;
            }
            tableHTML += "</table>";
            document.getElementById("table-container").innerHTML = tableHTML;
        }

        function plotChart(data) {
            let trace = {
                x: data.date,
                y: data.close,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: 'cyan', width: 2 },
                marker: { color: 'orange', size: 6 },
                name: 'Close Price'
            };
            Plotly.newPlot("stock-chart", [trace], { title: `📈 Stock Prices for ${data.year}` });
        }

        function plotVolumeChart(data) {
            let trace = {
                x: data.date,
                y: data.volume,
                type: 'bar',
                marker: { color: 'blue' },
                name: 'Volume'
            };
            Plotly.newPlot("volume-chart", [trace], { title: `📊 Trading Volume for ${data.year}` });
        }

        function plotCandlestickChart(data) {
            let trace = {
                x: data.date,
                close: data.close,
                open: data.open,
                high: data.high,
                low: data.low,
                type: 'candlestick',
                increasing: { line: { color: 'lime' } },
                decreasing: { line: { color: 'red' } },
                name: 'Candlestick'
            };
            Plotly.newPlot("candlestick-chart", [trace], { title: `🕯️ Candlestick Chart for ${data.year}` });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/get_data")
def get_data():
    year = request.args.get("year")

    try:
        year = int(year)
        df_filtered = df[df["Date"].dt.year == year].head(15)  # Display up to 15 rows

        if df_filtered.empty:
            return jsonify({"error": f"⚠️ No data found for year {year}"}), 404
        
        df_filtered["Price Diff"] = df_filtered["Close"] - df_filtered["Open"]
        df_filtered["% Change"] = ((df_filtered["Close"] - df_filtered["Open"]) / df_filtered["Open"]) * 100
        df_filtered["Trend"] = df_filtered.apply(lambda row: "Bullish" if row["Close"] > row["Open"] else "Bearish", axis=1)

        return jsonify({
            "year": year,
            "date": df_filtered["Date"].dt.strftime('%Y-%m-%d').tolist(),
            "open": df_filtered["Open"].tolist(),
            "high": df_filtered["High"].tolist(),
            "low": df_filtered["Low"].tolist(),
            "close": df_filtered["Close"].tolist(),
            "volume": df_filtered["Volume"].tolist(),
            "price_diff": df_filtered["Price Diff"].tolist(),
            "percent_change": df_filtered["% Change"].tolist(),
            "trend": df_filtered["Trend"].tolist()
        })

    except ValueError:
        return jsonify({"error": "❌ Invalid year input"}), 400

if __name__ == "__main__":
    app.run(debug=True)
