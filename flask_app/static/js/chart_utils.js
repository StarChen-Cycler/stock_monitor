let chart = null;
let subcharts = [];
let fetchedData = null;

// Add cache management functions
function saveToCache(tsCode, data) {
    try {
        // Create a deep copy of the data
        const cacheData = JSON.parse(JSON.stringify(data));
        
        // // Remove color configurations from strategies before caching
        // if (cacheData.strategies) {
        //     Object.keys(cacheData.strategies).forEach(strategyName => {
        //         if (cacheData.strategies[strategyName].config) {
        //             delete cacheData.strategies[strategyName].config;
        //         }
        //     });
        // }

        const cache = JSON.parse(localStorage.getItem('stockDataCache') || '{}');
        cache[tsCode] = {
            data: cacheData,
            timestamp: Date.now()
        };
        localStorage.setItem('stockDataCache', JSON.stringify(cache));
    } catch (e) {
        console.error('Error saving to cache:', e);
        localStorage.clear();
        try {
            const cache = {};
            cache[tsCode] = {
                data: cacheData,
                timestamp: Date.now()
            };
            localStorage.setItem('stockDataCache', JSON.stringify(cache));
        } catch (e) {
            console.error('Failed to save to cache even after clearing:', e);
        }
    }
}

function getFromCache(tsCode) {
    try {
        const cache = JSON.parse(localStorage.getItem('stockDataCache') || '{}');
        const cachedData = cache[tsCode];
        
        if (!cachedData) return null;

        // Check if cache is older than 24 hours
        const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
        if (Date.now() - cachedData.timestamp > CACHE_DURATION) {
            // Remove expired cache
            delete cache[tsCode];
            localStorage.setItem('stockDataCache', JSON.stringify(cache));
            return null;
        }

        // Force a fresh fetch of strategy configurations
        return null;  // Temporarily disable cache to force fresh data
    } catch (e) {
        console.error('Error reading from cache:', e);
        return null;
    }
}

function saveSettings() {
    const settings = {
        stockCode: $('#stockInput').val(),
        subchartCount: $('#subchartCount').val(),
        subchartSelections: {}
    };
    
    // Save all subchart selections, even if they're not currently visible
    $('.subchart-selector').each(function(index) {
        const id = $(this).attr('id');
        settings.subchartSelections[id] = $(this).val();
    });
    
    // Also save any previously saved selections that aren't currently in the DOM
    if (window.savedSubchartSelections) {
        Object.keys(window.savedSubchartSelections).forEach(key => {
            if (!settings.subchartSelections[key]) {
                settings.subchartSelections[key] = window.savedSubchartSelections[key];
            }
        });
    }
    
    localStorage.setItem('stockChartSettings', JSON.stringify(settings));
}

function loadSettings() {
    const savedSettings = localStorage.getItem('stockChartSettings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        
        $('#stockInput').val(settings.stockCode || '00001');
        $('#subchartCount').val(settings.subchartCount || '0');
        
        // Store selections in window for persistence
        window.savedSubchartSelections = settings.subchartSelections || {};
    }
}

$(document).ready(function() {
    loadSettings();
    searchStock();
    
    // Add resize observer for the chart container
    const chartContainer = document.querySelector('.chart-container');
    const resizeObserver = new ResizeObserver(entries => {
        if (chart) {
            chart.resize();
        }
    });
    resizeObserver.observe(chartContainer);

    // Add manual resize functionality
    const resizeHandle = document.querySelector('.resize-handle');
    let isResizing = false;
    let startY;
    let startHeight;

    resizeHandle.addEventListener('mousedown', function(e) {
        isResizing = true;
        startY = e.clientY;
        startHeight = chartContainer.clientHeight;
        chartContainer.classList.add('resizing');
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        const delta = e.clientY - startY;
        const newHeight = Math.max(300, Math.min(startHeight + delta, window.innerHeight - 100));
        chartContainer.style.height = newHeight + 'px';
        
        if (chart) {
            chart.resize();
        }
    });

    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            chartContainer.classList.remove('resizing');
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (chart) {
            chart.resize();
        }
    });

    $('#stockInput').on('change', saveSettings);
    $('#subchartCount').on('change', saveSettings);
});

function searchStock() {
    var tsCode = $('#stockInput').val().trim();
    if (!tsCode) {
        alert('Please enter a valid stock code');
        return;
    }

    // Try to get data from cache first
    const cachedData = getFromCache(tsCode);
    if (cachedData) {
        fetchedData = cachedData;
        updateSubchartSelectors();
        buildChart(cachedData.main, cachedData.strategies);
        return;
    }

    // If not in cache, fetch from server
    $.ajax({
        url: '/stock_data',
        method: 'GET',
        data: { ts_code: tsCode },
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                alert(data.error);
                return;
            }
            // Save to cache
            saveToCache(tsCode, data);
            
            fetchedData = data;
            updateSubchartSelectors();
            buildChart(data.main, data.strategies);
        },
        error: function(xhr, status, error) {
            alert('Error retrieving stock data');
            console.error("AJAX error:", error);
        }
    });
}

// Helper function to create initial configuration for charts and also for updating the chart
function setChartParams(subchartCount, mainData) {
    // Fixed pixel values for positioning and grid heights
    const chartContainer = document.getElementById('stockChart');
    const containerWidth = chartContainer.clientWidth;
    const leftMargin = 50;
    const rightMargin = 50;
    const gridWidth = containerWidth - leftMargin - rightMargin;
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
    // Initialize the main chart
    if (chart) {
        chart.dispose();
    }

    const chartContainer = document.getElementById('stockChart');
    chart = echarts.init(chartContainer);

    // Get chart configurations dynamically
    const subchartCount = parseInt($('#subchartCount').val());

    const { gridConfig, legendConfig, xAxisConfig, yAxisConfig, dataZoomConfig } = setChartParams(subchartCount, mainData);

    // Force chart resize to fit container
    chart.resize();

    const options = {
        animation: false,
        title: {
            text: 'Stock Candlestick Chart',
            top: '0%',
            left: 'left',
            textStyle: {
                color: '#ffffff'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                snap: true,
                crossStyle: { color: '#ffffff' },
                label: {
                    color: '#000000'
                }
            },
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            borderColor: '#333',
            textStyle: {
                color: '#ffffff'
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
                backgroundColor: '#777',
                color: '#ffffff'
            }
        },
        legend: {
            ...legendConfig[0],
            textStyle: {
                color: '#ffffff'
            }
        },
        grid: gridConfig,
        xAxis: xAxisConfig.map(axis => ({
            ...axis,
            axisLabel: {
                ...axis.axisLabel,
                color: '#ffffff'
            },
            axisLine: {
                ...axis.axisLine,
                lineStyle: {
                    color: '#ffffff'
                }
            },
            splitLine: {
                show: false
            }
        })),
        yAxis: yAxisConfig.map(axis => ({
            ...axis,
            axisLabel: {
                ...axis.axisLabel,
                color: '#ffffff'
            },
            axisLine: {
                ...axis.axisLine,
                lineStyle: {
                    color: '#ffffff'
                }
            },
            splitLine: {
                show: true,
                lineStyle: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            },
            splitArea: {
                show: true,
                areaStyle: {
                    color: ['rgba(255, 255, 255, 0.02)', 'rgba(255, 255, 255, 0.01)']
                }
            }
        })),
        dataZoom: dataZoomConfig.map(zoom => ({
            ...zoom,
            textStyle: {
                color: '#ffffff'
            },
            handleStyle: {
                ...zoom.handleStyle,
                color: '#ffffff'
            },
            borderColor: '#ffffff',
            dataBackground: {
                lineStyle: { color: '#ffffff' },
                areaStyle: { color: 'rgba(255, 255, 255, 0.2)' }
            },
            selectedDataBackground: {
                lineStyle: { color: '#ffffff' },
                areaStyle: { color: 'rgba(255, 255, 255, 0.4)' }
            }
        })),
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

    // Add MA lines from strategy data if available
    if (strategiesData.ma) {
        const maData = strategiesData.ma.data;
        const maConfig = strategiesData.ma.config.outputs;
        
        for (const [outputName, outputConfig] of Object.entries(maConfig)) {
            options.series.push({
                name: outputConfig.name,
                type: 'line',
                data: maData[outputName],
                smooth: true,
                lineStyle: { 
                    width: 2,
                    color: outputConfig.color
                },
                itemStyle: { 
                    color: outputConfig.color
                },
                showSymbol: false
            });
        }
    }

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

    // Add subchart series based on selected strategies
    for (let i = 0; i < subchartCount; i++) {
        const selectorId = `subchart${i + 1}`;
        const selectedStrategy = $(`#${selectorId}`).val();
        if (selectedStrategy && strategiesData[selectedStrategy] && selectedStrategy !== 'ma') {
            const strategyData = strategiesData[selectedStrategy];
            const outputs = strategyData.config.outputs;
            
            // Sort outputs by order if specified
            const sortedOutputs = Object.entries(outputs).sort((a, b) => 
                (a[1].order || 0) - (b[1].order || 0)
            );

            // Add each output as a series
            for (const [outputName, outputConfig] of sortedOutputs) {
                const isBarChart = outputConfig.type === 'bar';
                const isHistogram = outputConfig.use_color_from === 'histogram';

                // Create series configuration
                let seriesConfig = {
                    name: outputConfig.name,
                    type: outputConfig.type,
                    data: strategyData.data[outputName],
                    smooth: false,
                    showSymbol: false,
                    xAxisIndex: i + 1,
                    yAxisIndex: i + 1
                };

                // For bar charts, add color based on data type
                if (isBarChart) {
                    if (isHistogram) {
                        // For MACD histogram, color based on value
                        seriesConfig.itemStyle = {
                            color: function(params) {
                                return params.value >= 0 ? '#00da3c' : '#ec0000';
                            }
                        };
                    } else {
                        // For regular bars (like volume), color based on candlestick
                        seriesConfig.itemStyle = {
                            color: function(params) {
                                const candleData = mainData.candle_data[params.dataIndex];
                                return candleData[1] > candleData[0] ? '#00da3c' : '#ec0000';
                            }
                        };
                    }
                } else {
                    // For non-bar charts, use the strategy's configured color
                    seriesConfig.lineStyle = { 
                        width: 3,
                        color: outputConfig.color
                    };
                    seriesConfig.itemStyle = { 
                        color: outputConfig.color,
                        opacity: 0.8
                    };
                }

                options.series.push(seriesConfig);
            }
        }
    }

    // Set the final options
    chart.setOption(options);
}

function resetChart() {
    buildChart(fetchedData.main, fetchedData.strategies);
}

function updateSubcharts() {
    updateSubchartSelectors();
    resetChart();
}

function updateChartForSubchart(selectorId) {
    if (fetchedData) {
        buildChart(fetchedData.main, fetchedData.strategies);
    }
}

// Function to update subchart selectors based on subchartCount
function updateSubchartSelectors() {
    const subchartCount = parseInt($('#subchartCount').val());
    const selectorsContainer = $('.subchart-selectors-container');
    selectorsContainer.empty();

    // Create wrapper for selectors
    const selectorsWrapper = $('<div>', {
        class: 'selectors-wrapper',
        css: {
            display: 'flex',
            gap: '20px',
            alignItems: 'center'
        }
    });

    for (let i = 0; i < subchartCount; i++) {
        const selectorId = `subchart${i + 1}`;
        const selectorContainer = $('<div>', {
            css: {
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
            }
        });

        const label = $('<label>', {
            text: `Subchart ${i + 1}:`,
            for: selectorId,
            css: {
                color: 'white'
            }
        });

        const selector = $('<select>', {
            id: selectorId,
            class: 'subchart-selector',
            css: {
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                cursor: 'pointer',
                minWidth: '200px'
            }
        });

        selector.on('change', function() {
            const id = $(this).attr('id');
            if (!window.savedSubchartSelections) {
                window.savedSubchartSelections = {};
            }
            window.savedSubchartSelections[id] = $(this).val();
            updateChartForSubchart(this.id);
            saveSettings();
        });

        selectorContainer.append(label, selector);
        selectorsWrapper.append(selectorContainer);
    }

    selectorsContainer.append(selectorsWrapper);
    updateSubchartSelectorsOptions();
}

function updateSubchartSelectorsOptions() {
    if (!fetchedData || !fetchedData.strategies) return;

    const strategies = Object.keys(fetchedData.strategies);
    $('.subchart-selector').each(function(index) {
        const selectorId = this.id;
        $(this).empty();
        
        // Add placeholder option
        $('<option>', {
            value: '',
            text: 'Select strategy',
            css: {
                background: '#2c2c2c',
                color: 'white',
                padding: '8px'
            }
        }).appendTo(this);

        // Add strategy options
        strategies.forEach(strategy => {
            const strategyConfig = fetchedData.strategies[strategy].config || { name: strategy };
            $('<option>', {
                value: strategy,
                text: strategyConfig.name || strategy,
                css: {
                    background: '#2c2c2c',
                    color: 'white',
                    padding: '8px'
                }
            }).appendTo(this);
        });

        // Set saved value if available, otherwise default to first strategy
        if (window.savedSubchartSelections && window.savedSubchartSelections[selectorId]) {
            $(this).val(window.savedSubchartSelections[selectorId]);
        } else if (strategies.length > 0) {
            // Only set default if no saved selection exists
            const defaultStrategy = strategies[Math.min(index, strategies.length - 1)];
            $(this).val(defaultStrategy);
            // Save this default selection
            if (!window.savedSubchartSelections) {
                window.savedSubchartSelections = {};
            }
            window.savedSubchartSelections[selectorId] = defaultStrategy;
            saveSettings();
        }
    });

    // Update chart after populating options
    resetChart();
}
