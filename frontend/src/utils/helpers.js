// 清理交易对符号
export const cleanSymbol = (s) => {
  if (!s) return '';
  return s.toString().replace('/USDT', '').replace(':USDT', '');
};

// 计算搬砖利润
export const calculateSpreadProfit = (item, capital, feePercent) => {
  const spread = parseFloat(item.spread) || 0;
  const gross = capital * (spread / 100);
  const tradeFee = capital * 0.002; // 0.2% 交易费
  const withdrawFee = capital * (feePercent / 100);
  return (gross - tradeFee - withdrawFee).toFixed(2);
};

// 计算日收益
export const calculateDailyYield = (strategyType, item, amount, leverage) => {
  const total = amount * leverage;

  if (strategyType === 'spread') {
    const spread = parseFloat(item.spread) || 0;
    return (total * (spread / 100)).toFixed(2);
  } else if (strategyType === 'single') {
    const rateStr = item.rate.replace('%', '');
    const rate = parseFloat(rateStr) / 100;
    return (total * rate * 3).toFixed(4);
  } else if (strategyType === 'futures') {
    const aprDiff = parseFloat(item.apr_diff) || 0;
    return (total * (aprDiff / 100 / 365)).toFixed(4);
  }

  return '0.00';
};
