import React, { useState } from 'react'
import { useInterval } from '../utils/reactHooks'
import { startFetchingTickers } from './KunaAPI'
import CandleChart from '../components/CandleChart'
import Loader from '../components/Loader'

const Kuna = props => {
  const [candles, setCandles] = useState([])

  // TODO: Load history data, Kuna API V3
  // They use it on their site
  // https://api.kuna.io/v3/tv/history?symbol=btcuah&resolution=60&from=1582995207&to=1588179267
  // Use websocket wss://pusher.kuna.io/app/4b6a8b2c758be4e58868?protocol=7&client=js&version=3.0.0&flash=false
  useInterval(() => {
    startFetchingTickers({
      market: 'btcuah',
      timeFrame: '1m',
      onData: candle => setCandles([...candles, candle])
    })
  }, 1000)

  let content = <Loader />

  if (candles.length >= 3) {
    content = <CandleChart title={'Kuna BTC/UAH'} realData={candles}/>
  }

  return content
}

export default Kuna
