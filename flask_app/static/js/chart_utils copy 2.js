let chart = null;
let subcharts = [];

$(document).ready(function() {
    let fetchedData = null; // Declare a variable to hold the fetched data
    searchStock(fetchedData);
});

function searchStock() {
    console.log("searchStock() called");
    var tsCode = $('#stockInput').val().trim();
    if (!tsCode) {
        alert('Please enter a valid stock code');
        console.log("No stock code entered.");
        return;
    }

    // Fetch data and build chart
    $.ajax({
        url: '/stock_data',
        method: 'GET',
        data: { ts_code: tsCode },
        dataType: 'json',
        success: function(data) {
            console.log("Data received:", data);
            if (data.error) {
                alert(data.error);
                console.log("Error in data:", data.error);
                return;
            }
            fetchedData = data;
            updateSubchartSelectorsOptions(); 
            buildChart(data.main, data.strategies);
        },
        error: function(xhr, status, error) {
            alert('Error retrieving stock data');
            console.log("AJAX error:", error);
        }
    });
}

// Helper function to create initial configuration for charts and also for updating the chart
function setChartParams(subchartCount, mainData) {
    // Fixed pixel values for positioning and grid heights
    const chartHeight = 1200;  // Height of the chart container
    const mainChartHeight = 500;  // Main chart height (candlestick)
    const subchartHeight = 150;  // Each subchart (RSI, Volume) height
    const startPoint = 90;
    const endPoint = 100;
    // Calculate the bottom position for dataZoom to be below the last grid
    const totalHeight = mainChartHeight + (subchartCount * (subchartHeight + 5)); // Total height of all grids
    const dataZoomBottom = totalHeight + 80; // Adding some space between the last grid and dataZoom

    // Set grid configuration for all charts
    let gridConfig = [
        {
            left: 50,
            right: 50,
            top: 50, // Slightly under the legend
            height: mainChartHeight, // Height of the main chart

        }
    ];

    let legendConfig = [
        {
            data: ['Candlestick', 'MA5', 'MA10', 'MA20', 'RSI', 'Volume'],
            top: 10, // Positioning legend slightly near the top
            left: 'center'
        }
    ];

    let xAxisConfig = [
        {
            type: 'category',
            data: mainData.x_data,
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false }
        },
    ];

    let yAxisConfig = [
        {
            scale: true,
            splitArea: { show: true }
        }
    ];

    let dataZoomConfig = [
        {
            type: 'slider',
            show: true,
            xAxisIndex: [0],
            filterMode: 'filter',
            height: 30,
            top: dataZoomBottom, // Dynamically set the bottom position
            handleSize: '80%',
            handleStyle: { color: '#d3dee5' },
            backgroundStyle: { color: '#f8fcff' },
            dataBackground: { lineStyle: { color: '#5793f3' }, areaStyle: { color: '#e3f6ff' } },
            start: startPoint,
            end: endPoint
        },
        {
            type: 'inside',
            xAxisIndex: [0,1,2,3,4,5],
            start: startPoint,
            end: endPoint
            
        }
    ];

    // Dynamically add subcharts based on subchartCount
    let subchartTop = mainChartHeight + 60;  // Subchart positions (starting below the main chart)
    for (let i = 0; i < subchartCount; i++) {
        let gridIndex = i + 1;
        gridConfig.push({
            left: 50,
            right: 50,
            top: subchartTop + (i * (subchartHeight)) + 10, // Stack subcharts vertically
            height: subchartHeight,
        });

        // Add new x and y axes for each subchart
        xAxisConfig.push({
            type: 'category',
            gridIndex: gridIndex,
            data: mainData.x_data,
            boundaryGap: false,
            axisLine: { onZero: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            min: 'dataMin',
            max: 'dataMax'
        });

        yAxisConfig.push({
            scale: true,
            gridIndex: gridIndex,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: true }
        });
    }

    
    
    return { gridConfig, legendConfig, xAxisConfig, yAxisConfig, dataZoomConfig};
}

function buildChart(mainData, strategiesData) {
    console.log("Building chart...");

    // Initialize the main chart
    if (chart) {
        console.log("Disposing of existing chart before reinitializing.");
        chart.dispose();
    }

    chart = echarts.init(document.getElementById('stockChart'));
    console.log("Main chart initialized.");

    // Get chart configurations dynamically
    const subchartCount = parseInt($('#subchartCount').val());
    console.log("Subchart count:", subchartCount);

    const { gridConfig, legendConfig, xAxisConfig, yAxisConfig,dataZoomConfig} = setChartParams(subchartCount, mainData);

    const options = {
        animation: false,
        title: {
            text: 'Stock Candlestick Chart',
            top: '0%',
            left: 'left'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                snap: true,
                crossStyle: { color: '#ffffff' }
            },
            formatter: function (params) {
                let tooltip = '';
                if (!params || params.length === 0) return tooltip;
                tooltip += params[0].name + '<br>';
                params.forEach(param => {
                    if (param.seriesType === 'candlestick') {
                        const [num, open, close, low, high] = param.value;
                        tooltip += `Open=${open.toFixed(2)}<br>Close=${close.toFixed(2)}<br>Low=${low.toFixed(2)}<br>High=${high.toFixed(2)}<br>`;
                    } else {
                        tooltip += `${param.seriesName}: ${param.value.toFixed(2)}<br>`;
                    }
                });
                return tooltip;
            }
        },
        axisPointer: {
            link: [
                { xAxisIndex: 'all' }
            ],
            label: {
                backgroundColor: '#777'
            }
        },
        legend: legendConfig[0], // Dynamically set legend configuration
        grid: gridConfig, // Dynamically set grid configuration
        xAxis: xAxisConfig, // Dynamically set xAxis configuration
        yAxis: yAxisConfig, // Dynamically set yAxis configuration
        dataZoom: dataZoomConfig, // Dynamically set dataZoom configuration
        series: [{
            name: 'Candlestick',
            type: 'candlestick',
            data: mainData.candle_data,
            itemStyle: {
                color: '#00da3c',
                color0: '#ec0000',
                borderColor: '#00da3c',
                borderColor0: '#ec0000'
            }
        }]
    };

    // Calculate MA Lines
    const maSeries = [{
        name: 'MA5',
        type: 'line',
        data: mainData.ma5,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#ff4500' },
        showSymbol: false
    }, {
        name: 'MA10',
        type: 'line',
        data: mainData.ma10,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#06a7a0' },
        showSymbol: false
    }, {
        name: 'MA20',
        type: 'line',
        data: mainData.ma20,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#3c763d' },
        showSymbol: false
    }];

    options.series.push(...maSeries);

    // Add MarkPoints
    options.series[0].markPoint = {
        label: {
            formatter: (param) => Math.round(param.value) || 0,
            color: '#000000'
        },
        data: [{
            name: '最高',
            type: 'max',
            valueDim: 'highest',
            symbol: 'pin',
            symbolSize: 40,
            itemStyle: {
                color: 'yellow'
            }
        }, {
            name: '最低',
            type: 'min',
            valueDim: 'lowest',
            symbol: 'pin',
            symbolRotate: 180,
            symbolOffset: [0, 0],
            symbolSize: 40,
            itemStyle: {
                color: 'yellow'
            },
            label: {
                offset: [0, 10]
            }
        }]
    };

    // // Add Subcharts (RSI and Volume) if available
    // // Dynamically add strategies to the chart based on the selected subchart count
    // if (subchartCount >= 1 && strategiesData.rsi) {
    //     options.series.push({
    //         name: 'RSI',
    //         type: 'line',
    //         data: strategiesData.rsi,
    //         smooth: false,
    //         lineStyle: { width: 1 },
    //         itemStyle: { color: '#ff00ff' },
    //         showSymbol: false,
    //         xAxisIndex: 1,  // Sync with the subchart x-axis
    //         yAxisIndex: 1   // Sync with the subchart y-axis
    //     });
    // }

    // // Dynamically add strategies to the chart based on the selected subchart count
    // if (subchartCount >= 2 && strategiesData.days_since_highest_vol) {
    //     options.series.push({
    //         name: 'Days Since Highest Volume',
    //         type: 'line',
    //         data: strategiesData.days_since_highest_vol,
    //         smooth: false,
    //         lineStyle: { width: 1 },
    //         itemStyle: { color: '#ff0000' },
    //         showSymbol: false,
    //         xAxisIndex: 2,  // Sync with the subchart x-axis
    //         yAxisIndex: 2   // Sync with the subchart y-axis
    //     });
    //     console.log("Days Since Highest Volume data added to chart.");
    // }
    // // Dynamically add strategies to the chart based on the selected subchart count
    // if (subchartCount >= 3 && strategiesData.days_since_lowest_vol) {
    //     options.series.push({
    //         name: 'Days Since Lowest Volume',
    //         type: 'line',
    //         data: strategiesData.days_since_lowest_vol,
    //         smooth: false,
    //         lineStyle: { width: 1 },
    //         itemStyle: { color: '#0000ff' },
    //         showSymbol: false,
    //         xAxisIndex: 3,  // Sync with the subchart x-axis
    //         yAxisIndex: 3   // Sync with the subchart y-axis
    //     });
    //     console.log("Days Since Lowest Volume data added to chart.");
    // }
    // // Dynamically add strategies to the chart based on the selected subchart count
    // if (subchartCount >= 4 && strategiesData.volume) {
    //     options.series.push({
    //         name: 'Volume',
    //         type: 'bar',
    //         data: strategiesData.volume,
    //         smooth: false,
    //         lineStyle: { width: 1 },
    //         itemStyle: { color: '#0f00ff' },
    //         showSymbol: false,
    //         xAxisIndex: 4,  // Sync with the subchart x-axis
    //         yAxisIndex: 4   // Sync with the subchart y-axis
    //     });
    //     console.log("Volume data added to chart.");
    // }

    for (let i = 0; i < subchartCount; i++) {
        const selectorId = `subchart${i + 1}`;
        const selectedStrategy = $(`#${selectorId}`).val();
        if (selectedStrategy && strategiesData[selectedStrategy]) {
            const seriesName = selectedStrategy;
            options.series.push({
                name: seriesName,
                type: selectedStrategy === 'volume' ? 'bar' : 'line',
                data: strategiesData[selectedStrategy],
                smooth: false,
                lineStyle: { width: 1 },
                itemStyle: { color: getColorForStrategy(seriesName) },
                showSymbol: false,
                xAxisIndex: i + 1,
                yAxisIndex: i + 1
            });
            console.log(`${seriesName} data added to chart.`);
        }
    }

    // Set the final options
    chart.setOption(options);
    console.log("Chart options applied.");
}

function resetChart() {
    console.log("resetChart() called");
    buildChart(fetchedData.main, fetchedData.strategies);
}

function updateSubcharts() {
    console.log("updateSubcharts() called.");
    updateSubchartSelectors()
    resetChart();
}

function updateChartForSubchart(selectorId) {
    console.log(`Subchart selector ${selectorId} changed.`);
    resetChart(); 
}


// // Function to update subchart selectors based on subchartCount
// function updateSubchartSelectors() {
//     console.log("11111111111111111111111")
//     const subchartCount = parseInt($('#subchartCount').val());
//     const selectorsContainer = $('.subchart-selectors-container');
//     selectorsContainer.empty(); // Clear existing selectors

//     for (let i = 0; i < subchartCount; i++) {
//         const selector = $('<select>', {
//             id: `subchart${i + 1}`,
//             class: 'subchart-selector',
//             onchange: 'updateSubcharts()'
//         });

//         // If data is available, populate options
//         if (fetchedData && fetchedData.strategies) {
//             const strategies = Object.keys(fetchedData.strategies);
//             strategies.forEach(strategy => {
//                 $('<option>', {
//                     value: strategy,
//                     text: strategy
//                 }).appendTo(selector);
//             });
//         }

//         selectorsContainer.append(selector);
//     }
// }

// // Function to populate selector options when data is fetched
// function updateSubchartSelectorsOptions() {
//     if (!fetchedData || !fetchedData.strategies) return;

//     const strategies = Object.keys(fetchedData.strategies);
//     $('.subchart-selector').each(function(index) {
//         $(this).empty(); // Clear existing options
//         strategies.forEach(strategy => {
//             $('<option>', {
//                 value: strategy,
//                 text: strategy
//             }).appendTo(this);
//         });
//         // Default to first strategy
//         $(this).val(strategies[0]).change();
//     });
// }


// function getColorForStrategy(strategyName) {
//     switch (strategyName) {
//         case 'rsi': return '#ff00ff';
//         case 'days_since_highest_vol': return '#ff0000';
//         case 'days_since_lowest_vol': return '#0000ff';
//         case 'volume': return '#0f00ff';
//         default: return '#000000';
//     }
// }

// Function to update subchart selectors based on subchartCount
function updateSubchartSelectors() {
    const subchartCount = parseInt($('#subchartCount').val());
    const selectorsContainer = $('.subchart-selectors-container');
    selectorsContainer.empty();

    for (let i = 0; i < subchartCount; i++) {
        const selector = $('<select>', {
            id: `subchart${i + 1}`,
            class: 'subchart-selector',
            onchange: function () {
                // Only update the chart for this specific subchart, no need to call updateSubcharts
                updateChartForSubchart(this.id); 
            }
        });

        if (fetchedData && fetchedData.strategies) {
            const strategies = Object.keys(fetchedData.strategies);
            strategies.forEach(strategy => {
                $('<option>', {
                    value: strategy,
                    text: strategy
                }).appendTo(selector);
            });
        }

        selectorsContainer.append(selector);
    }
}

// Function to populate selector options when data is fetched
function updateSubchartSelectorsOptions() {
    if (!fetchedData || !fetchedData.strategies) return;

    const strategies = Object.keys(fetchedData.strategies);
    $('.subchart-selector').each(function(index) {
        $(this).empty(); // Clear existing options
        strategies.forEach(strategy => {
            $('<option>', {
                value: strategy,
                text: strategy
            }).appendTo(this);
        });
        // Default to first strategy
        $(this).val(strategies[0]).change();
    });
}

function getColorForStrategy(strategyName) {
    switch (strategyName) {
        case 'rsi': return '#ff00ff';
        case 'days_since_highest_vol': return '#ff0000';
        case 'days_since_lowest_vol': return '#0000ff';
        case 'volume': return '#0f00ff';
        default: return '#000000';
    }
}