(function e(t,n,r) {
  function s(o,u){
    if(!n[o]){
      if(!t[o]){
        var a = typeof require=="function"&&require;
        if(!u&&a) return a(o,!0);
        if(i) return i(o,!0);
        var f = new Error("Cannot find module '"+o+"'");
        throw f.code="MODULE_NOT_FOUND",f
      }
      var l=n[o]={exports:{}};
      t[o][0].call(l.exports,function(e){
        var n=t[o][1][e];
        return s(n?n:e)
      },l,l.exports,e,t,n,r)
    }
    return n[o].exports
  }
  var i=typeof require=="function"&&require;
  for(var o=0;o<r.length;o++)
    s(r[o]);
  return s
})
({1:[function(require,module,exports){
    "use strict";
    /* global require, module, d3 */

    var configurable = require('./util/configurable');

    var defaultConfig = {
      xScale: null,
      dateFormat: null
    };

    module.exports = function (d3) {

      return function (config) {

        config = config || {};
        for (var key in defaultConfig) {
          config[key] = config[key] || defaultConfig[key];
        }

        function delimiter(selection) {
          selection.each(function (data) {
            d3.select(this).selectAll('text').remove();

            var limits = config.xScale.domain();

//상단날짜
            d3.select(this).append('text')
                .text(function () {

                  return config.dateFormat(limits[0]);
                })
                .classed('start', true)
            ;

            d3.select(this).append('text')
                .text(function () {

                  return config.dateFormat(limits[1]);
                })
                .attr('text-anchor', 'end')
                .attr('transform', 'translate(' + config.xScale.range()[1] + ')')
                .classed('end', true)
            ;
          });
        }

        configurable(delimiter, config);

        return delimiter;
      };
    };

  },{"./util/configurable":6}],2:[function(require,module,exports){
    "use strict";
    /* global require, module */

    var configurable = require('./util/configurable');
    var xAxisFactory = require('./xAxis');

    module.exports = function (d3) {
      var eventLine = require('./eventLine')(d3);
      var delimiter = require('./delimiter')(d3);

      var defaultConfig = {
        start: new Date(0),
        end: new Date(),
        minScale: 0,
        maxScale: Infinity,
        width: 1000,
        margin: {
          top: 60,
          left: 100,
          bottom: 40,
          right: 25
        },
        locale: null,
        axisFormat: null,
        tickFormat: [
          [".%L", function(d) { return d.getMilliseconds(); }],
          [":%S", function(d) { return d.getSeconds(); }],
          ["%I:%M", function(d) { return d.getMinutes(); }],
          ["%I %p", function(d) { return d.getHours(); }],
          ["%a %d", function(d) { return d.getDay() && d.getDate() != 1; }],
          ["%b %d", function(d) { return d.getDate() != 1; }],
          ["%B", function(d) { return d.getMonth(); }],
          ["%Y", function() { return true; }]
        ],
        eventHover: null,
        eventZoom: null,
        eventClick: null,
        hasDelimiter: true,
        hasTopAxis: true,
        hasBottomAxis: function (data) {
          return data.length >= 10;
        },
        eventLineColor: 'black',
        eventColor: null
      };

      return function eventDrops (config) {
        var xScale = d3.time.scale();
        var yScale = d3.scale.ordinal();
        config = config || {};
        for (var key in defaultConfig) {
          config[key] = config[key] || defaultConfig[key];
        }

        function eventDropGraph (selection) {
          selection.each(function (data) {
            var zoom = d3.behavior.zoom().center(null).scaleExtent([config.minScale, config.maxScale]).on("zoom", updateZoom);

            zoom.on("zoomend", zoomEnd);

            var graphWidth = config.width - config.margin.right - config.margin.left;
            var graphHeight = data.length * 40; //그래프 높이
            var height = graphHeight + config.margin.top + config.margin.bottom;

            var xAxisTop, xAxisBottom;

            d3.select(this).select('svg').remove();

            var svg = d3.select(this)
                .append('svg')
                .attr('width', config.width)
                .attr('height', height)
            ;

            var graph = svg.append('g')
                .attr('transform', 'translate(0, 25)');

            var yDomain = [];
            var yRange = [];

            data.forEach(function (event, index) {
              yDomain.push(event.name);
              yRange.push(index * 40);
            });

            yScale.domain(yDomain).range(yRange);

            var yAxisEl = graph.append('g')
                .classed('y-axis', true)
                .attr('transform', 'translate(0, 60)');

            var yTick = yAxisEl.append('g').selectAll('g').data(yDomain);

            yTick.enter()
                .append('g')
                .attr('transform', function(d) {
                  return 'translate(0, ' + yScale(d) + ')';
                })
                .append('line')
                .classed('y-tick', true)
                .attr('x1', config.margin.left)
                .attr('x2', config.margin.left + graphWidth);

            yTick.exit().remove();

            var curx, cury;
            var zoomRect = svg
                .append('rect')
                .call(zoom)
                .classed('zoom', true)
                .attr('width', graphWidth)
                .attr('height', height )
                .attr('transform', 'translate(' + config.margin.left + ', 35)')
            ;
//mouse over 해당 점 정보
            if (typeof config.eventHover === 'function') {
              zoomRect.on('mousemove', function(d, e) {
                var event = d3.event;
                if (curx == event.clientX && cury == event.clientY) return;
                curx = event.clientX;
                cury = event.clientY;
                zoomRect.attr('display', 'none');
                var el = document.elementFromPoint(d3.event.clientX, d3.event.clientY);
                zoomRect.attr('display', 'block');
                if (el.tagName !== 'circle') return;
                config.eventHover(el);
              });
            }

            if (typeof config.eventClick === 'function') {
              zoomRect.on('click', function () {
                zoomRect.attr('display', 'none');
                var el = document.elementFromPoint(d3.event.clientX, d3.event.clientY);
                zoomRect.attr('display', 'block');
                if (el.tagName !== 'circle') return;
                config.eventClick(el);
              });
            }

            xScale.range([0, graphWidth]).domain([config.start, config.end]);

            zoom.x(xScale);

            function updateZoom() {
              if (d3.event.sourceEvent && d3.event.sourceEvent.toString() === '[object MouseEvent]') {
                zoom.translate([d3.event.translate[0], 0]);
              }

              if (d3.event.sourceEvent && d3.event.sourceEvent.toString() === '[object WheelEvent]') {
                zoom.scale(d3.event.scale);
              }

              redraw();
            }

            // initialization of the delimiter
            svg.select('.delimiter').remove();
            var delimiterEl = svg
                .append('g')
                .classed('delimiter', true)
                .attr('width', graphWidth)
                .attr('height', 10)
                .attr('transform', 'translate(' + config.margin.left + ', ' + (config.margin.top - 45) + ')')
                .call(delimiter({
                  xScale: xScale,
                  dateFormat: config.locale ? config.locale.timeFormat("%d %B %Y %p %I:%M:%S.%L" ) : d3.time.format("%d %B %Y %p %I:%M:%S.%L")
                }))
            ;

            function redrawDelimiter() {

              delimiterEl.call(delimiter({
                xScale: xScale,
                dateFormat: config.locale ? config.locale.timeFormat("%d %B %Y %p %I:%M:%S.%L") : d3.time.format("%d %B %Y %p %I:%M:%S.%L")
              }))
              ;
            }

            function zoomEnd() {
              if (config.eventZoom) {
                config.eventZoom(xScale);
              }
              if (config.hasDelimiter) {
                redrawDelimiter(xScale);
              }
            }

            var hasTopAxis = typeof config.hasTopAxis === 'function' ? config.hasTopAxis(data) : config.hasTopAxis;
            if (hasTopAxis) {
              xAxisTop = xAxisFactory(d3, config, xScale, graph, graphHeight, 'top');
            }

            var hasBottomAxis = typeof config.hasBottomAxis === 'function' ? config.hasBottomAxis(data) : config.hasBottomAxis;
            if (hasBottomAxis) {
              xAxisBottom = xAxisFactory(d3, config, xScale, graph, graphHeight, 'bottom');
            }



            // initialization of the graph body
            zoom.size([config.width, height]);

            graph.select('.graph-body').remove();
            var graphBody = graph
                .append('g')
                .classed('graph-body', true)
                .attr('transform', 'translate(' + config.margin.left + ', ' + (config.margin.top - 15) + ')');

            var lines = graphBody.selectAll('g').data(data);

            lines.enter()
                .append('g')
                .classed('line', true)
                .attr('transform', function(d) {
                  return 'translate(0,' + yScale(d.name) + ')';
                })
                .style('fill', config.eventLineColor)
                .call(eventLine({ xScale: xScale, eventColor: config.eventColor }))
            ;

            lines.exit().remove();

            function redraw() {

              var hasTopAxis = typeof config.hasTopAxis === 'function' ? config.hasTopAxis(data) : config.hasTopAxis;
              if (hasTopAxis) {
                xAxisTop.drawXAxis();
              }

              var hasBottomAxis = typeof config.hasBottomAxis === 'function' ? config.hasBottomAxis(data) : config.hasBottomAxis;
              if (hasBottomAxis) {
                xAxisBottom.drawXAxis();
              }

              lines.call(eventLine({ xScale: xScale, eventColor: config.eventColor }));
            }

            redraw();
            if (config.hasDelimiter) {
              redrawDelimiter(xScale);
            }
            if (config.eventZoom) {
              config.eventZoom(xScale);
            }
          });
        }

        configurable(eventDropGraph, config);

        return eventDropGraph;
      };
    };

  },{"./delimiter":1,"./eventLine":3,"./util/configurable":6,"./xAxis":7}],3:[function(require,module,exports){
    "use strict";
    /* global require, module, d3 */

    var configurable = require('./util/configurable');
    var filterData = require('./filterData');

    var defaultConfig = {
      xScale: null
    };

    module.exports = function (d3) {
      return function (config) {

        config = config || {
          xScale: null,
          eventColor: null
        };
        for (var key in defaultConfig) {
          config[key] = config[key] || defaultConfig[key];
        }

        var eventLine = function eventLine(selection) {
          selection.each(function (data) {
            d3.select(this).selectAll('text').remove();

            d3.select(this).append('text')
                .text(function(d) {
                  var count = filterData(d.dates, config.xScale).length;
                  return d.name + (count > 0 ? ' (' + count + ')' : '');
                })
                .attr('text-anchor', 'end')
                .attr('transform', 'translate(-20)')
                .style('fill', 'black')
            ;

            d3.select(this).selectAll('circle').remove();

            var circle = d3.select(this).selectAll('circle')
                .data(function(d) {
                  // filter value outside of range
                  return filterData(d.dates, config.xScale);
                });

            circle.enter()
                .append('circle')
                .attr('cx', function(d) {
                  return config.xScale(d);
                })
                .style('fill', config.eventColor)
                .attr('cy', -5)
                .attr('r', 5)
            ;

            circle.exit().remove();

          });
        };

        configurable(eventLine, config);

        return eventLine;
      };
    };

  },{"./filterData":4,"./util/configurable":6}],4:[function(require,module,exports){
    "use strict";
    /* global module */

    module.exports = function filterData(data, scale) {
      data = data || [];
      var filteredData = [];
      var boundary = scale.range();
      var min = boundary[0];
      var max = boundary[1];
      data.forEach(function (datum) {
        var value = scale(datum);
        if (value < min || value > max) {
          return;
        }
        filteredData.push(datum);
      });

      return filteredData;
    };

  },{}],5:[function(require,module,exports){
    "use strict";
    /* global require, define, module */

    var eventDrops = require('./eventDrops');

    if (typeof define === "function" && define.amd) {
      define('d3.chart.eventDrops', ["d3"], function (d3) {
        d3.chart = d3.chart || {};
        d3.chart.eventDrops = eventDrops(d3);
      });
    } else if (window) {
      window.d3.chart = window.d3.chart || {};
      window.d3.chart.eventDrops = eventDrops(window.d3);
    } else {
      module.exports = eventDrops;
    }

  },{"./eventDrops":2}],6:[function(require,module,exports){
    module.exports = function configurable(targetFunction, config, listeners) {
      listeners = listeners || {};
      for (var item in config) {
        (function(item) {
          targetFunction[item] = function(value) {
            if (!arguments.length) return config[item];
            config[item] = value;
            if (listeners.hasOwnProperty(item)) {
              listeners[item](value);
            }

            return targetFunction;
          };
        })(item); // for doesn't create a closure, forcing it
      }
    };

  },{}],7:[function(require,module,exports){


    module.exports = function (d3, config, xScale, graph, graphHeight, where) {
      var xAxis = {};
      var xAxisEls = {};

      var tickFormatData = [];

      config.tickFormat.forEach(function (item) {
        var tick = item.slice(0);
        tickFormatData.push(tick);
      });

      var tickFormat = config.locale ? config.locale.timeFormat.multi(tickFormatData) : d3.time.format.multi(tickFormatData);
      xAxis[where] = d3.svg.axis()
          .scale(xScale)
          .orient(where)
          .tickFormat(tickFormat)
      ;

      if (typeof config.axisFormat === 'function') {
        config.axisFormat(xAxis);
      }

      var y = (where == 'bottom' ? parseInt(graphHeight) : 0) + config.margin.top - 40;

      xAxisEls[where] = graph
          .append('g')
          .classed('x-axis', true)
          .classed(where, true)
          .attr('transform', 'translate(' + config.margin.left + ', ' + y + ')')
          .call(xAxis[where])
      ;

      var drawXAxis = function drawXAxis() {
        xAxisEls[where]
            .call(xAxis[where])
        ;
      };

      return {
        drawXAxis: drawXAxis
      };
    };

  },{}]},{},[5])





var chartPlaceholder = document.getElementById('chart_placeholder');

var data = [

  { name: "보행자", dates: [], img:[],  color: "blue" },
  { name: "신호등", dates: [] , img:[], color: "red" },
  { name: "자동차", dates: [], img:[], color: "yellow"  },
  { name: "가로등", dates: [], img:[], color: "green"  },
  { name: "표지판", dates: [], img:[], color: "black"  },
  { name: "횡단보도", dates: [], img:[], color: "pink"  },
  { name: "전봇대", dates: [], img:[], color: "purple"  },
];
console.log(data)

//data time -> 현재 가지고있는 currenttime으로 변경
var endTime = Date.now();
var oneMonth = 30 * 24 * 60 * 60 * 1000;
console.log(oneMonth)
var startTime = endTime - oneMonth;
console.log(endTime)

// data 생성
// for (var i=0; i<data.length; i++){
//   //max object 개수 model에서 사람 labe가진 수
//   var max =  Math.floor(Math.random() * 160) + 50;
//   for (var j = 0; j < max; j++) {
//     var time = startTime;
//     data[i].dates.push(new Date(time));
//     console.log(startTime)
//
//   }
// }
// console.log(data);

function ggetTimeLine(video_pk, url){
  console.log(video_pk)
  try {
    // var defaultData = []
    // var query_length_tag_1 = [];
    // console.log (query_length_tag_1)
    // var test;
    // console.log(test)
    $.ajax({
      method: "GET",
      url: url,
      data:{
        'video_pk' : video_pk,
      },
      success: function (test_data) {
        //코드수정 필요 (for문)
        query_length_tag_1 = test_data['query_length_tag_1'];
        query_length_tag_2 = test_data['query_length_tag_2'];
        query_length_tag_3 = test_data['query_length_tag_3'];
        query_length_tag_4 = test_data['query_length_tag_4'];
        query_length_tag_5 = test_data['query_length_tag_5'];
        query_length_tag_6 = test_data['query_length_tag_6'];
        query_length_tag_7 = test_data['query_length_tag_7'];
        // for (var i=0; i<data.length; i++){
        // var max =  Math.floor(Math.random() * 160) + 50;
        object_list_1 = test_data['object_list_1'];
        object_list_2 = test_data['object_list_2'];
        object_list_3 = test_data['object_list_3'];
        object_list_4 = test_data['object_list_4'];
        object_list_5 = test_data['object_list_5'];
        object_list_6 = test_data['object_list_6'];
        object_list_7 = test_data['object_list_7'];

        var max0 = query_length_tag_1 //객체 개수 받아와야함
        var max1 = query_length_tag_2
        var max2 = query_length_tag_3
        var max3 = query_length_tag_4
        var max4 = query_length_tag_5
        var max5 = query_length_tag_6
        var max6 = query_length_tag_7

        var time0 = object_list_1
        var time1 = object_list_2
        var time2 = object_list_3
        var time3 = object_list_4
        var time4 = object_list_5
        var time5 = object_list_6
        var time6 = object_list_7




        for (var j = 0; j < max0; j++) {
          // var tt = time0[j]
          // console.log(tt)
          // var current_dt = Number(tt)
          // data[0].dates.push(new Date(current_dt));
          // console.log(data[0])
          var time = Math.floor((Math.random() * oneMonth)) + startTime

          var image = object_list_1[(max0+1)*j+1]

          data[0].dates.push(new Date(time));
          data[0].img.push(image);
          //console.log(image)
          //console.log(data[0].dates.push(new Date(time)))
          //console.log(new Date(time))
        }

        for (var j = 0; j < max1; j++) {

          //data format 맞춰줘야합
          var time = Math.floor((Math.random() * oneMonth)) + startTime
          data[1].dates.push(new Date(time));
          // console.log(time)
          // }
        }
        for (var j = 0; j < max2; j++) {

          //data format 맞춰줘야합
          var time = Math.floor((Math.random() * oneMonth)) + startTime
          data[2].dates.push(new Date(time));
          // console.log(time)
          // }
        }
        for (var j = 0; j < max3; j++) {

          //data format 맞춰줘야합
          var time = Math.floor((Math.random() * oneMonth)) + startTime
          data[3].dates.push(new Date(time));
          // console.log(time)
          // }
        }
        for (var j = 0; j < max4; j++) {

          //data format 맞춰줘야합
          var time = Math.floor((Math.random() * oneMonth)) + startTime
          data[4].dates.push(new Date(time));
          // console.log(time)
          // }
        }
        for (var j = 0; j < max5; j++) {

          //data format 맞춰줘야합
          var time = Math.floor((Math.random() * oneMonth)) + startTime
          data[5].dates.push(new Date(time));
          // console.log(time)
          // }
        }
        for (var j = 0; j < max6; j++) {

          //data format 맞춰줘야합
          var time = Math.floor((Math.random() * oneMonth)) + startTime
          data[6].dates.push(new Date(time));
          // console.log(time)
          // }
        }

      },
      error: function (error_data) {
        console.log("error")
        console.log(error_data)
      }
    })

  }
  catch(e){
    console.log("fail!!!")
  }
}
///////////////////////////////////////////////////////



//information
var eventDropsChart = d3.chart.eventDrops();
eventDropsChart.start(new Date(startTime))
    .width(1100)
    .end(new Date(endTime))
    .minScale(0.5)
    .maxScale(100)
    .axisFormat(function(xAxis) {
      xAxis.top.ticks(7);
    })
    .eventLineColor(function(e){
      // console.log(e);
      return e.color;
    })
    .eventHover(function(el) {
      var series = el.parentNode.firstChild.innerHTML;
      var timestamp = d3.select(el).data()[0];
      console.log(d3.select(el))
      console.log(d3.select())
      //console.log(series)
      //console.log(timestamp)


      document.getElementById('legend').innerHTML = 'Hovering [' + timestamp + '] in series "' + series + '"'; //information

    });



d3.select('#chart_placeholder')
    .datum(data)
    .call(eventDropsChart);


