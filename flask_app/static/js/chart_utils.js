let chart = null;
let subcharts = [];
let fetchedData = null;

// Add cache management functions
function saveToCache(tsCode, data) {
    try {
        const cache = JSON.parse(localStorage.getItem('stockDataCache') || '{}');
        cache[tsCode] = {
            data: data,
            timestamp: Date.now()
        };
        localStorage.setItem('stockDataCache', JSON.stringify(cache));
    } catch (e) {
        console.error('Error saving to cache:', e);
        // If localStorage is full, clear it and try again
        localStorage.clear();
        try {
            const cache = {};
            cache[tsCode] = {
                data: data,
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

        return cachedData.data;
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
    
    window.addEventListener('resize', function() {
        if (chart) {
            chart.resize();
        }
    });

    $('#stockInput').on('change', saveSettings);
    $('#subchartCount').on('change', saveSettings);
});

function searchStock() {
    console.log("searchStock() called");
    var tsCode = $('#stockInput').val().trim();
    if (!tsCode) {
        alert('Please enter a valid stock code');
        console.log("No stock code entered.");
        return;
    }

    // Try to get data from cache first
    const cachedData = getFromCache(tsCode);
    if (cachedData) {
        console.log("Using cached data for", tsCode);
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
            console.log("Data received from server:", data);
            if (data.error) {
                alert(data.error);
                console.log("Error in data:", data.error);
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
            console.log("AJAX error:", error);
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

    const { gridConfig, legendConfig, xAxisConfig, yAxisConfig, dataZoomConfig } = setChartParams(subchartCount, mainData);

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
        legend: legendConfig[0],
        grid: gridConfig,
        xAxis: xAxisConfig,
        yAxis: yAxisConfig,
        dataZoom: dataZoomConfig,
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

    // Add subchart series based on selected strategies
    for (let i = 0; i < subchartCount; i++) {
        const selectorId = `subchart${i + 1}`;
        const selectedStrategy = $(`#${selectorId}`).val();
        
        if (selectedStrategy && strategiesData[selectedStrategy]) {
            const strategyData = strategiesData[selectedStrategy];
            if (strategyData.error) {
                console.error(`Error with strategy ${selectedStrategy}:`, strategyData.error);
                continue;
            }

            const config = strategyData.config || {
                type: 'line',
                color: '#000000',
                name: selectedStrategy
            };

            options.series.push({
                name: config.name,
                type: config.type,
                data: strategyData.data,
                smooth: false,
                lineStyle: { width: 1 },
                itemStyle: { color: config.color },
                showSymbol: false,
                xAxisIndex: i + 1,
                yAxisIndex: i + 1
            });
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
    updateSubchartSelectors();
    resetChart();
}

function updateChartForSubchart(selectorId) {
    console.log(`Subchart selector ${selectorId} changed.`);
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
