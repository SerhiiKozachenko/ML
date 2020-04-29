import { timeFormat, utcParse  } from 'd3-time-format'

const KUNA_API = 'https://kuna.io/api/v2'
const parseUnixTime = utcParse('%s')
const formatTimeFrame = (timeFrame = '1m') => {
  if (timeFrame === '1m') {
    return timeFormat('%Y-%m-%d %H:%M')
  } else {
    throw new Error(`formatTimeFrame(${timeFrame}) - unsupported period.`)
  }
}

// contains OHLC objects
let candlesticks = []
// contains the current candlestick OHLC
let candle = null
// last time and price processed info - used to detect changes
let lastTickerTime = null
let lastTickerPrice = null

// https://kuna.io/documents/api?lang=ua
export const startFetchingTickers =
  async ({ market = 'btcuah', timeFrame = '1m', onData = (candle) => {} }) => {
    const res = await fetch(`${KUNA_API}/tickers/${market}`)
    let ticker = await res.json()
    ticker.at = parseUnixTime(ticker.at)
    const tickerTime = formatTimeFrame(timeFrame)(ticker.at)
    const tickerPrice = Number(ticker.ticker.last)
    if (lastTickerTime === tickerTime && lastTickerPrice === tickerPrice) {
      return
    }

    if (lastTickerTime !== tickerTime) {
      if (candle) {
        onData({ ...candle })
      }

      // New timeframe started - create a new candlestick
      candle = {
        date: ticker.at,
        open: tickerPrice,
        high: tickerPrice,
        low: tickerPrice,
        close: tickerPrice
      }
      candlesticks.push(candle)
      console.debug(`New time frame (${timeFrame}) started: `, candle)
    } else if (lastTickerPrice !== tickerPrice) {
      // Price changed - update current candlestick
      candle.high = Math.max(candle.high, tickerPrice)
      candle.low = Math.min(candle.low, tickerPrice)
      candle.close = tickerPrice
      console.debug(`Current time frame (${timeFrame}) updated: `, candle)
    }
    // Update last tracked values
    lastTickerTime = tickerTime
    lastTickerPrice = tickerPrice
}
