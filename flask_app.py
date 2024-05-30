from flask import Flask, request, jsonify  # 引入 Flask 相關模組
from flask_cors import CORS  # 引入處理跨域請求的模組
import requests  # 用於發送 HTTP 請求
from bs4 import BeautifulSoup  # 用於解析 HTML 內容

app = Flask(__name__)  # 初始化 Flask 應用程式  
CORS(app)  # 處理跨域請求

def scrape_stock_data(股票代碼):
    """
    爬取股票資料的函數
    
    Args:
        股票代碼 (str): 股票代碼
    
    Returns:
        dict: 包含股票資料的字典格式
    """
    def scrape_dividend_data():
        網址 = f'https://tw.stock.yahoo.com/quote/{股票代碼}.TW/dividend'  # Yahoo股票網頁的URL
        response = requests.get(網址)  # 發送HTTP GET請求取得網頁內容

        try:
            response.raise_for_status()  # 檢查HTTP請求狀態碼是否為200，否則拋出異常
            soup = BeautifulSoup(response.content, 'html.parser')  # 使用BeautifulSoup解析HTML內容

            # 獲取股利所屬期間的資料
            times = soup.find_all("div", class_="D(f) W(88px) Ta(start)")
            dividend_periods = [time.text.strip() for time in times[2:]] if times else []  # 只保留第三筆以後的股利所屬期間資料

            # 獲取所有股利金額的資料
            moneys = soup.find_all("div", class_="Fxg(1) Fxs(1) Fxb(0%) Ta(end) Mend(0):lc Mend(12px) W(72px) Miw(72px)")
            all_cash_dividends = [money.text.strip() for money in moneys[4:]] if moneys else []  # 只保留第五筆以後的股利金額資料

            more_times = soup.find_all("div", class_="Fxg(1) Fxs(1) Fxb(0%) Ta(end) Mend(0):lc Mend(12px) W(88px) Miw(88px)")
            判斷值 = [time.text.strip() for time in more_times] if more_times else []  # 所有的股利所屬期間資料

            print("爬取的更多股利所屬期間資料:", 判斷值)
            print("爬取的股利所屬期間資料:", dividend_periods[:5])
            print("爬取的股利金額資料:", all_cash_dividends[:22])

            # 根據判斷值選擇不同的資料處理方式
            if any('Q' in 判斷 for 判斷 in 判斷值):
                processed_cash_dividends = process_cash_dividends_20(all_cash_dividends)
            else:
                processed_cash_dividends = process_cash_dividends_4(all_cash_dividends)

            total_cash_dividends = sum(processed_cash_dividends[:5])

            # 計算便宜價、合理價和昂貴價
            便宜價 = round((total_cash_dividends * len(processed_cash_dividends)) / 7, 2)
            合理價 = round((total_cash_dividends * len(processed_cash_dividends)) / 5, 2)
            昂貴價 = round((total_cash_dividends * len(processed_cash_dividends)) / 3, 2)

            data = {
                'dividend_periods_357': dividend_periods[:5],
                'cash_dividends_357': processed_cash_dividends[:5],
                'dividend_periods_di': dividend_periods[:10],
                'cash_dividends_di': processed_cash_dividends[:10],
                'cheap_price': 便宜價,
                'fair_price': 合理價,
                'expensive_price': 昂貴價
            }

            return {'success': True, 'data': data}

        except requests.RequestException as e:
            return {'success': False, 'message': f'Request failed: {e}'}

    def process_cash_dividends_20(all_cash_dividends):
        processed_cash_dividends = []
        for i in range(0, len(all_cash_dividends), 20):
            chunk = all_cash_dividends[i:i+20]  # 每20個資料為一循環

            # 前2個資料若有不是數值的以0取代，後面18個資料也以0取代，然後將20個資料加總
            processed_chunk = [float(dividend) if dividend.replace('.', '', 1).isdigit() else 0 for dividend in chunk[:2]]
            processed_chunk.extend([0] * 18)  # 後面18個資料以0取代
            total_chunk = sum(processed_chunk)
            processed_cash_dividends.append(total_chunk)

        return processed_cash_dividends

    def process_cash_dividends_4(all_cash_dividends):
        processed_cash_dividends = []
        for i in range(0, len(all_cash_dividends), 4):
            chunk = all_cash_dividends[i:i+4]  # 每4個資料為一循環

            # 前2個資料若有不是數值的以0取代，後面2個資料也以0取代，然後將4個資料加總
            processed_chunk = [float(dividend) if dividend.replace('.', '', 1).isdigit() else 0 for dividend in chunk[:2]]
            processed_chunk.extend([0] * 2)  # 後面2個資料以0取代
            total_chunk = sum(processed_chunk)
            processed_cash_dividends.append(total_chunk)

        return processed_cash_dividends

    return scrape_dividend_data()  # 回傳爬取的股票資料


@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    stock_code = request.json.get('stockCode')  # 从POST请求中获取股票代码
    stock_data = scrape_stock_data(stock_code)  # 调用函数爬取股票数据
    return jsonify(stock_data)  # 将股票数据以JSON格式返回

if __name__ == '__main__':
    app.run(debug=True)  # 运行在本地的127.0.0.1:5000，启用Debug模式
#這是後端程式碼