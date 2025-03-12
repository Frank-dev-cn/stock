from xtquant import xtdata
from xtquant import xttrader
from xtquant.xttype import StockAccount
import numpy as np
import pandas as pd
import time
import datetime

class QMTStockSwapTrader:
    def __init__(self, source_stock, target_stock, total_volume, swap_period_days=5):
        """
        初始化QMT换股交易策略
        
        参数:
        - source_stock: 原始股票代码
        - target_stock: 目标股票代码
        - total_volume: 总计划交易股数
        - swap_period_days: 换股时间跨度(天数)
        """
        # 连接QMT交易系统
        self.xt_trader = xttrader.XtTrader()
        self.xt_trader.connect()
        
        # 获取股票账户
        self.stock_account = StockAccount('你的证券账户')
        
        self.source_stock = source_stock
        self.target_stock = target_stock
        self.total_volume = total_volume
        self.swap_period_days = swap_period_days
        
        # 动态分段交易量计算
        self.trade_segments = self._calculate_trade_segments()
    
    def _calculate_trade_segments(self):
        """
        根据正态分布生成分段交易策略，避免集中交易
        """
        # 生成正态分布的交易量权重
        weights = np.random.normal(
            loc=0.5, 
            scale=0.15, 
            size=self.swap_period_days
        )
        weights = np.abs(weights) / np.sum(np.abs(weights))
        
        # 根据权重分配交易量
        segments = [int(self.total_volume * w) for w in weights]
        
        # 处理可能的四舍五入误差
        segments[-1] += (self.total_volume - sum(segments))
        
        return segments
    
    def _get_current_price(self, stock_code):
        """获取股票当前价格"""
        # 使用xtdata获取实时价格
        price_data = xtdata.get_stock_bars('1d', stock_code)
        return price_data['close'][-1] if len(price_data) > 0 else None
    
    def _place_order(self, stock_code, order_type, volume):
        """
        下单函数
        
        参数:
        - stock_code: 股票代码
        - order_type: 'buy' 或 'sell'
        - volume: 交易数量
        """
        # 获取当前价格
        current_price = self._get_current_price(stock_code)
        
        if current_price is None:
            print(f"无法获取 {stock_code} 的价格")
            return False
        
        # 计算市价委托价格
        # 买入时略微提高价格，卖出时略微降低价格，减少市场冲击
        if order_type == 'sell':
            price = current_price * 0.99  # 略低于市价
        else:
            price = current_price * 1.01  # 略高于市价
        
        # 下单
        try:
            order_params = {
                'market': 'stock',
                'stock_code': stock_code,
                'price': price,
                'volume': volume,
                'order_type': xttrader.XANT_ORDER_TYPE_LIMIT
            }
            
            order_id = self.xt_trader.order(self.stock_account, **order_params)
            
            print(f"{order_type.upper()} {volume} 股 {stock_code}，价格 {price}")
            return order_id
        except Exception as e:
            print(f"下单失败: {e}")
            return False
    
    def execute_swap(self):
        """
        执行平稳换股策略
        """
        print(f"开始执行 {self.source_stock} 到 {self.target_stock} 的换股策略")
        
        trade_log = []
        for i, volume in enumerate(self.trade_segments, 1):
            # 卖出source股票
            sell_result = self._place_order(self.source_stock, 'sell', volume)
            
            if sell_result:
                trade_log.append({
                    'date': datetime.datetime.now(),
                    'action': 'SELL',
                    'stock': self.source_stock,
                    'volume': volume
                })
            
            # 等待一段时间，模拟交易间隔
            time.sleep(np.random.uniform(1, 3))
            
            # 买入target股票
            buy_result = self._place_order(self.target_stock, 'buy', volume)
            
            if buy_result:
                trade_log.append({
                    'date': datetime.datetime.now(),
                    'action': 'BUY',
                    'stock': self.target_stock,
                    'volume': volume
                })
            
            # 两次交易间额外等待
            time.sleep(np.random.uniform(1, 3))
        
        return pd.DataFrame(trade_log)
    
    def __del__(self):
        """
        关闭交易连接
        """
        if hasattr(self, 'xt_trader'):
            self.xt_trader.disconnect()

def main():
    swap_trader = QMTStockSwapTrader(
        source_stock='600519',   # 贵州茅台
        target_stock='000858',   # 五粮液
        total_volume=10000,      # 总交易量
        swap_period_days=5       # 换股天数
    )
    
    trade_results = swap_trader.execute_swap()
    print("换股交易日志:")
    print(trade_results)

if __name__ == "__main__":
    main()