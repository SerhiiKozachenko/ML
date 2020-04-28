import React, { useState, useEffect, useRef } from 'react';
import { timeFormat, timeParse, utcParse  } from "d3-time-format";
import logo from './logo.svg';
import './App.css';
import Chart from './Chart'

import rawData from './data.json'
const initData = rawData.map(i => ({...i, date: new Date(i.date)}))

function useInterval(callback, delay) {
  const savedCallback = useRef();

  // Remember the latest callback.
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval.
  useEffect(() => {
    function tick() {
      savedCallback.current();
    }
    if (delay !== null) {
      let id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

// contains OHLC objects for each minute
let minute_candlesticks = []
// contains the current minute candlestick OHLC
let current_min_candlestick = {}
// last minute and price processed info - used to detect changes
let last_tick_min = null
let last_tick_price = null

// var timeParse = utcParse("%Y-%m-%dT%H:%M:%S")
const parseUnixTime = utcParse("%s")
const formatTimeStr = timeFormat("%Y-%m-%d %H:%M")

function App(props) {

  const [realData, setData] = useState(
    []
    // initData
    );


    useInterval(() => {
      const myAsyncFn = async () => {
        const res = await fetch("https://kuna.io/api/v2/tickers/btcuah")
        let tick = await res.json()
        tick.at = parseUnixTime(tick.at)
        const tick_min = formatTimeStr(tick.at)
        const tick_price = tick.ticker.last
        // console.log(tick_min, tick_price)
        if (last_tick_min === tick_min && last_tick_price === tick_price)
          return
  
        if (last_tick_min !== tick_min) {
          // update state
          if (minute_candlesticks.length) {
            debugger
            if (!realData.length) {
              setData([...minute_candlesticks])
            } else {
              const last_min_temp = minute_candlesticks[minute_candlesticks.length - 1];
              const last_min_state = realData[realData.length - 1];
              if (last_min_temp.date !== last_min_state.date) {
                setData([...realData, last_min_temp])
              }
            }
            
          }
  
          // New minute started - create a new candlestick
          current_min_candlestick = {
              "date": tick.at,
            "open": tick_price,
            "high": tick_price,
             "low": tick_price,
           "close": tick_price
          }
          minute_candlesticks.push(current_min_candlestick)
          console.log("New minute started: ", current_min_candlestick)
        } else if (last_tick_price !== tick_price) {
          // Price changed - update current candlestick
          current_min_candlestick["high"] = Math.max(current_min_candlestick["high"], tick_price)
          current_min_candlestick["low"] = Math.min(current_min_candlestick["low"], tick_price)
          current_min_candlestick["close"] = tick_price
          console.log("Current minute updated: ", current_min_candlestick)
        }
        // Update last tracked values
        last_tick_min = tick_min
        last_tick_price = tick_price
      }
      myAsyncFn()
    }, 1000);
  
  return (
    <div className="App">
      <header className="App-header">
        {/* <img src={logo} className="App-logo" alt="logo" /> */}
        <h1>
          Trading Signals
        </h1>
        
        <Chart realData={realData}/>
     </header>
    </div>
  );
}

export default App;
