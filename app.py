

from flask import Flask, render_template, request
import os
import yfinance as yf
import pandas as pd

app = Flask(__name__)
@app.route('/')
def hello_world():
    # URL of the Google Sheets document
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSUAVjQ4CoPwfIyVzdS6jp22XvnJs6m8W05hag1xUXKo5TrgjbYTIggJxP8TO6spPRCKi5l4sMyPXBr/pub?output=xlsx'

    # Fetch data from Google Sheets using Pandas
    allCompanyData = pd.read_excel(url).values.tolist()

    # Render the template with fetched data
    return render_template('index.html', allCompanyData=allCompanyData)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/stock_data', methods=['POST', 'GET'])
def stockFun():

    UserTicker_data = request.form.get('searchOutput')
    ticker = UserTicker_data.upper()

    # COMPANY INFORMATION
    try:
        # Get company information using yfinance
        companyInfo = yf.Ticker(ticker).info
        companyInfo = pd.DataFrame.from_dict(companyInfo, orient='index', columns=['Value']).reset_index()
        companyInfo.columns = ['Attribute', 'Value']
        companyName = companyInfo[companyInfo['Attribute'] == 'longName']['Value'].iloc[0]
        companyInfo = companyInfo.to_html(index=True)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        companyInfo = e

    # STOCK HISTORY
    try:
        stockHistory = yf.Ticker(UserTicker_data).history(period='10y')
        stockHistory = stockHistory.reset_index()
        stockHistory = stockHistory.to_json(orient='records')
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        stockHistory = e

    # DIVIDEND
    dividend = yf.Ticker(UserTicker_data).actions
    dividend.drop(columns=['Stock Splits'], inplace=True, errors='ignore')

    try:
        dividend = dividend[dividend['Dividends'] > 0]
        dividend = dividend.reset_index()
        dividend = dividend.to_json(orient='records')
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        dividend = e

    # NET INCOME
    try:
        incomeStmtJson = yf.Ticker(ticker).income_stmt
        incomeStmtJson.columns = incomeStmtJson.columns.tolist()
        incomeStmtJson = incomeStmtJson.to_html(index=True)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        incomeStmtJson = e

    # MAJOR HOLDERS
    try:
        majorHolders = yf.Ticker(ticker).major_holders
        majorHolders.columns = ['Percentage', 'Holders']
        majorHolders = majorHolders.to_html(index=False)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        majorHolders = e

    # INSTITUTIONAL HOLDERS
    try:
        institutionalHolders = yf.Ticker(ticker).institutional_holders
        institutionalHolders.columns = institutionalHolders.columns.tolist()
        institutionalHolders = institutionalHolders.to_html(index=False)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        institutionalHolders = e

    # INSTITUTIONAL HOLDERS PIE CHART
    try:
        institutionalHoldersPie = yf.Ticker(ticker).institutional_holders
        institutionalHoldersPie.columns = ['Holders', 'Shares', 'Date Reported', '% Out', 'Value']
        institutionalHoldersPie = institutionalHoldersPie.to_dict(orient='records')
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        institutionalHoldersPie = e

    # MUTUAL FUND HOLDERS PIE CHART
    try:
        mutualFundHoldersPie = yf.Ticker(ticker).mutualfund_holders
        mutualFundHoldersPie.columns = ['Holders', 'Shares', 'Date Reported', '% Out', 'Value']
        mutualFundHoldersPie = mutualFundHoldersPie.to_dict(orient='records')
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        mutualFundHoldersPie = e

    # NEWS
    try:
        newsData = yf.Ticker(ticker).news
        newsData = pd.DataFrame(newsData)
        newsData['link'] = newsData['link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
        newsData = newsData.to_html(index=False, columns=['title', 'relatedTickers', 'link'], escape=False, header=True)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        newsData = e

    # CANDLE CHART AND VOLUME
    try:
        candleChart = yf.download(ticker, group_by="ticker", period='1d', interval='5m')
        candleChart.reset_index(inplace=True)
        candleChart = candleChart.to_json(orient='records', date_format='iso')
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        candleChart = e

    try:
        VolumeData = yf.download(ticker, group_by="ticker", period='10y')
        VolumeData.reset_index(inplace=True)
        VolumeData = VolumeData.to_json(orient='records', date_format='iso')
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        VolumeData = e

    # Render the template with fetched data
    return render_template('index1.html', companyName=companyName, companyInfo=companyInfo,
                           incomeStmtJson=incomeStmtJson, VolumeData=VolumeData, stockHistory=stockHistory,
                           dividend=dividend, majorHolders=majorHolders, candleChart=candleChart,
                           institutionalHolders=institutionalHolders,
                           institutionalHoldersPie=institutionalHoldersPie, newsData=newsData,
                           mutualFundHoldersPie=mutualFundHoldersPie)

if __name__ == '__main__':
    app.run()
