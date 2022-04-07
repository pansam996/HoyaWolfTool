from pybit import HTTP
import time
from datetime import datetime


def bybitTool (API_KEY, SECRET, minutes):
    # start = time.time()

    session = HTTP("https://api.bybit.com",api_key=API_KEY, api_secret=SECRET)

    # GET the symbol list
    symbol_list = []
    query_symbol_data = session.query_symbol()['result']
    for i in query_symbol_data:
        name = i['name']
        if 'USDT' in name:
            symbol_list.append(name)

    
    utcT = datetime.utcnow() # get utc time to compare

    newOrderList = []
    symbolRecord = []
    for s in symbol_list:
        queryResult = session.get_active_order(symbol=s)['result']['data']
        if queryResult != None:
            for idx in range(len(queryResult)):
                queryT = queryResult[idx]['updated_time']
                queryT = datetime.strptime(queryT, "%Y-%m-%dT%H:%M:%SZ")

                if ((utcT - queryT).seconds // 60) > minutes:
                    break
                else:
                    if queryResult[idx]['order_status'] == 'Filled':
                        if s not in symbolRecord:
                            s_info = {}
                            s_info['symbol'] = s
                            s_info['last_exec_price'] = queryResult[idx]['last_exec_price']
                            newOrderList.append(s_info)
                            symbolRecord.append(s)
                            break
    
    
    if len(newOrderList) == 0:
        return []
    else:
        # Check the position by symbol list
        position_list = []
        for s_info in newOrderList:
            query_position = session.my_position(symbol=s_info['symbol'])['result']
            # check witch side
            for qp in query_position:
                if qp['size'] != 0 :
                    p_data = {}
                    p_data['symbol'] = qp['symbol'] # 標的
                    p_data['side'] = qp['side'] # 多 or 空
                    p_data['size'] = qp['size'] # 倉位
                    p_data['entry_price'] = qp['entry_price'] # 進場價格
                    p_data['leverage'] = qp['leverage'] # 槓桿倍數
                    p_data['take_profit'] = qp['take_profit'] # 止盈價格
                    p_data['stop_loss'] = qp['stop_loss'] # 止損價格
                    p_data['status'] = 'HOLD' # 持有
                    position_list.append(p_data)
                else: # 倉位空了 代表賣了
                    p_data = {}
                    p_data['symbol'] = qp['symbol'] # 標的
                    p_data['leave_price'] = s_info['last_exec_price']
                    p_data['status'] = 'SOLD' # 售出
                    position_list.append(p_data)
                    break
                    

    
        return position_list

    # end = time.time()
    # print("執行時間：%f 秒" % (end - start))


