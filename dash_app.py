import dash
from dash import dcc, html, Output, Input, State
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from utils.tse_tools import get_all_market

app = dash.Dash(__name__)
app.title = "📊 نمودار زنده قیمت"

app.layout = html.Div(style={
    "backgroundColor": "#f9f9f9",
    "padding": "40px",
    "fontFamily": "Segoe UI, Tahoma, sans-serif"
}, children=[

    html.H1("📈 نمودار زنده مممد", style={
        "color": "#333333",
        "textAlign": "center",
        "marginBottom": "30px"
    }),

    html.Div([
        dcc.Input(
            id="symbol-input",
            type="text",
            value="شستا",
            debounce=True,
            placeholder="نماد مورد نظر را وارد کنید...",
            style={
                "padding": "10px",
                "fontSize": "18px",
                "width": "300px",
                "marginBottom": "20px",
                "borderRadius": "8px",
                "border": "1px solid #ccc",
                "textAlign": "center"
            }
        )
    ], style={"textAlign": "center"}),

    html.Div([
        dcc.Graph(id='live-price-chart', config={'displayModeBar': False}),
    ], style={
        "backgroundColor": "#ffffff",
        "borderRadius": "10px",
        "padding": "20px",
        "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.1)"
    }),

    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0),

    dcc.Store(id='price-history', data={
        "timestamp": [],
        "close_price": [],
        "last_trade": [],
        "symbol": "شستا"
    }),

    html.Div(id="error", style={
        "color": "#cc0000",
        "marginTop": "15px",
        "textAlign": "center",
        "fontWeight": "bold"
    })
])

@app.callback(
    Output('price-history', 'data'),
    Output('error', 'children'),
    Input('interval-component', 'n_intervals'),
    State('price-history', 'data'),
    State('symbol-input', 'value')
)
def update_data(n, data, symbol):
    try:
        df = get_all_market("stocks_call_put")
        row = df[df["symbol"] == symbol]

        if row.empty:
            return data, f"⚠️ نماد «{symbol}» یافت نشد."

        close_price = row.iloc[0]["close_price"]
        last_trade = row.iloc[0]["last_trade"]
        now = datetime.now().strftime("%H:%M:%S")

        if data["symbol"] != symbol:
            # ریست در صورت تغییر نماد
            data = {
                "timestamp": [],
                "close_price": [],
                "last_trade": [],
                "symbol": symbol
            }

        data["timestamp"].append(now)
        data["close_price"].append(close_price)
        data["last_trade"].append(last_trade)

        data["timestamp"] = data["timestamp"][-100:]
        data["close_price"] = data["close_price"][-100:]
        data["last_trade"] = data["last_trade"][-100:]

        return data, ""

    except Exception as e:
        return data, f"❌ خطا در دریافت یا پردازش داده‌ها: {e}"

@app.callback(
    Output('live-price-chart', 'figure'),
    Input('price-history', 'data')
)
def update_chart(data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["timestamp"],
        y=data["close_price"],
        mode='lines+markers',
        name='قیمت پایانی',
        line=dict(color='#ff3636')
    ))

    fig.add_trace(go.Scatter(
        x=data["timestamp"],
        y=data["last_trade"],
        mode='lines+markers',
        name='آخرین معامله',
        line=dict(color='#00d962')
    ))

    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#333333'),
        xaxis_title='⏱ زمان',
        yaxis_title='💰 قیمت',
        title=f"📊 نمودار لحظه‌ای سهم: {data.get('symbol', '')}",
        title_x=0.5,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
