import React from 'react'
import { format } from 'd3-format'
import { timeFormat } from 'd3-time-format'
import { ChartCanvas, Chart } from 'react-stockcharts'
import {
	BarSeries,
	CandlestickSeries,
	LineSeries
} from 'react-stockcharts/lib/series'
import { XAxis, YAxis } from 'react-stockcharts/lib/axes'
import { EdgeIndicator } from 'react-stockcharts/lib/coordinates'
import { discontinuousTimeScaleProvider } from 'react-stockcharts/lib/scale'
import { HoverTooltip } from 'react-stockcharts/lib/tooltip'
import { ema } from 'react-stockcharts/lib/indicator'
import { fitWidth } from 'react-stockcharts/lib/helper'
import { last } from 'react-stockcharts/lib/utils'

// More charts here:
// https://github.com/rrag/react-stockcharts-examples2
// https://codesandbox.io/s/github/rrag/react-stockcharts-examples2/tree/master/examples/CandleStickChartWithHoverTooltip?file=/src/Chart.js
// https://codesandbox.io/s/github/rrag/react-stockcharts-examples2/tree/master/examples/CandleStickChartWithInteractiveIndicator?file=/src/Chart.js

const dateFormat = timeFormat('%Y-%m-%d %H:%M')
const numberFormat = format('.2f')

const tooltipContent = (ys) => {
	return ({ currentItem, xAccessor }) => {
		return {
			x: dateFormat(xAccessor(currentItem)),
			y: [{
					label: 'open',
					value: currentItem.open && numberFormat(currentItem.open)
				}, {
					label: 'high',
					value: currentItem.high && numberFormat(currentItem.high)
				}, {
					label: 'low',
					value: currentItem.low && numberFormat(currentItem.low)
				}, {
					label: 'close',
					value: currentItem.close && numberFormat(currentItem.close)
				}].concat(
					ys.map(each => ({
						label: each.label,
						value: each.value(currentItem),
						stroke: each.stroke
					}))
				).filter(line => line.value)
		}
	}
}

const ema20 = ema()
  .id(0)
  .options({ windowSize: 20 })
  .merge((d, c) => { d.ema20 = c })
  .accessor(d => d.ema20)

const ema50 = ema()
  .id(2)
  .options({ windowSize: 50 })
  .merge((d, c) => { d.ema50 = c })
  .accessor(d => d.ema50)

const xScaleProvider =
  discontinuousTimeScaleProvider
    .inputDateAccessor(d => d.date)

const CandleChart = props => {
  const calculatedData = ema50(ema20(props.realData))

  const { data, xScale, xAccessor, displayXAccessor } = xScaleProvider(
    calculatedData
  )

  // TODO: -150 - pull the history data?
  const start = xAccessor(last(data))
  // the window is at most 150 records
  const e = (data.length - 150) > 0 ? (data.length - 150) : data.length - data.length
  const end = xAccessor(data[Math.max(0, e)])

  if (props.realData.length < 3) {
    // console.log('realData < 3 wait')
    return <h3>Not enough data.</h3>
  }

  // TODO: Make it config via props, time frame - 1min, 5min, 30min, 1H, 6H, 12H, 1D, 1M etc.
  // EMA - 50, 200,
  // VOLUME
  // console.log('realData > 3 render chart!')
  return (
    <>
      <h3 style={{paddingLeft: '50px'}}>{props.title} {props.realData[props.realData.length - 1].close}</h3>
      <ChartCanvas
        height={400}
        width={props.width}
        ratio={props.ratio}
        margin={{ left: 80, right: 80, top: 30, bottom: 50 }}
        type={'hybrid'}
        seriesName='MSFT'
        data={data}
        xScale={xScale}
        xAccessor={xAccessor}
        displayXAccessor={displayXAccessor}
        xExtents={[start, end]}>
        <Chart
          id={1}
          yExtents={[d => [d.high, d.low], ema20.accessor(), ema50.accessor()]}
          padding={{ top: 10, bottom: 20 }}>

          <XAxis axisAt='bottom' orient='bottom' />
          <YAxis axisAt='right' orient='right' ticks={5} />

          <CandlestickSeries />

          <LineSeries yAccessor={ema20.accessor()} stroke={ema20.stroke()} />
          <LineSeries yAccessor={ema50.accessor()} stroke={ema50.stroke()} />

          <EdgeIndicator
            itemType='last'
            orient='right'
            edgeAt='right'
            yAccessor={d => d.close}
            fill={d => (d.close > d.open ? '#6BA583' : '#FF0000')}
          />

          <HoverTooltip
            yAccessor={ema50.accessor()}
            tooltipContent={tooltipContent(
              [{
                label: `${ema20.type()}(${ema20.options().windowSize})`,
                value: d => numberFormat(ema20.accessor()(d)),
                stroke: ema20.stroke()
              }, {
                label: `${ema50.type()}(${ema50.options().windowSize})`,
                value: d => numberFormat(ema50.accessor()(d)),
                stroke: ema50.stroke()
              }])}
            fontSize={15}
          />
        </Chart>
        {/* Volume bar chart */}
        {/* <Chart
          id={2}
          yExtents={[d => d.volume]}
          height={150}
          origin={(w, h) => [0, h - 150]}
        >
          <YAxis
            axisAt='left'
            orient='left'
            ticks={5}
            tickFormat={format('.2s')}
          />

          <BarSeries
            yAccessor={d => d.volume}
            fill={d => (d.close > d.open ? '#6BA583' : '#FF0000')}
          />
        </Chart> */}
      </ChartCanvas>
    </>
  )
}

export default fitWidth(CandleChart)
