export function formatNumber(number, decimalPlaces = 5) {
  let roundedNumber = number.toFixed(decimalPlaces); // 保留指定的小数位数
  let trimmedNumber = parseFloat(roundedNumber); // 将字符串转换为数字，去除末尾的零

  return trimmedNumber.toString(); // 返回格式化后的数字字符串
}
