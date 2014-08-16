nv.models.stackedAreaChart = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var stacked = nv.models.stackedArea()
    , xAxis = nv.models.axis()
    , yAxis = nv.models.axis()
    , legend = nv.models.legend()
    , controls = nv.models.legend()
    , interactiveLayer = nv.interactiveGuideline()
    ;

  var margin = {top: 20, right: 20, bottom: 60, left: 60}
    , width = null
    , height = null
    , color = nv.utils.defaultColor() // a function that takes in d, i and returns color
    , showControls = false
    , showLegend = true
    , showXAxis = true
    , showYAxis = true
    , rightAlignYAxis = false
    , useInteractiveGuideline = true
    , tooltips = true
    , tooltip = function(key, x, y, e, graph) {
        return '<h3>' + key + '</h3>' +
               '<p>' +  y + ' on ' + x + '</p>'
      }
    , x //can be accessed via chart.xScale()
    , y //can be accessed via chart.yScale()
    , yAxisTickFormat = d3.format(',f')
    , state = { style: stacked.style() }
    , defaultState = null
    , noData = 'No Data Available.'
    , dispatch = d3.dispatch('tooltipShow', 'tooltipHide', 'stateChange', 'changeState')
    , controlWidth = 250
    , cData = ['Stacked','Stream','Expanded']
    , controlLabels = {}
    , transitionDuration = 250
    ;

  xAxis
    .orient('bottom')
    .tickPadding(7)
    ;
  yAxis
    .orient((rightAlignYAxis) ? 'right' : 'left')
    ;

  controls.updateState(false);
  //============================================================


  //============================================================
  // Private Variables
  //------------------------------------------------------------

  var showTooltip = function(e, offsetElement) {
    var left = e.pos[0] + ( offsetElement.offsetLeft || 0 ),
        top = e.pos[1] + ( offsetElement.offsetTop || 0),
        x = xAxis.tickFormat()(stacked.x()(e.point, e.pointIndex)),
        y = yAxis.tickFormat()(stacked.y()(e.point, e.pointIndex)),
        content = tooltip(e.series.key, x, y, e, chart);

    nv.tooltip.show([left, top], content, e.value < 0 ? 'n' : 's', null, offsetElement);
  };

  //============================================================


  function chart(selection) {
    selection.each(function(data) {
      var container = d3.select(this),
          that = this;

      var availableWidth = (width  || parseInt(container.style('width')) || 900)
                             - margin.left - margin.right,
          availableHeight = (height || parseInt(container.style('height')) || 600)
                             - margin.top - margin.bottom;

      chart.update = function() { container.transition().duration(transitionDuration).call(chart); };
      chart.container = this;

      //set state.disabled
      state.disabled = data.map(function(d) { return !!d.disabled });

      if (!defaultState) {
        var key;
        defaultState = {};
        for (key in state) {
          if (state[key] instanceof Array)
            defaultState[key] = state[key].slice(0);
          else
            defaultState[key] = state[key];
        }
      }

      //------------------------------------------------------------
      // Display No Data message if there's nothing to show.

      if (!data || !data.length || !data.filter(function(d) { return d.values.length }).length) {
        var noDataText = container.selectAll('.nv-noData').data([noData]);

        noDataText.enter().append('text')
          .attr('class', 'nvd3 nv-noData')
          .attr('dy', '-.7em')
          .style('text-anchor', 'middle');

        noDataText
          .attr('x', margin.left + availableWidth / 2)
          .attr('y', margin.top + availableHeight / 2)
          .text(function(d) { return d });

        return chart;
      } else {
        container.selectAll('.nv-noData').remove();
      }

      //------------------------------------------------------------


      //------------------------------------------------------------
      // Setup Scales

      x = stacked.xScale();
      y = stacked.yScale();

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

d3.select('#chart1').selectAll("rect").data(d3.range(1))
        .enter()
        .append('rect')
            .style("opacity", 0.4)
            .attr("fill", "#d4d4d4")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("x", "0")
            .attr("y", "0")
            .attr("rx", "5")
            .attr("ry", "5");

      var wrap = container.selectAll('g.nv-wrap.nv-stackedAreaChart').data([data]);
      var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-stackedAreaChart').append('g');
      var g = wrap.select('g').attr("class", "test");

    //Drop shadow for hover--------------------

      var defs = gEnter.append("defs");

      var filter = defs.append("filter")
        .attr("id", "drop-shadow")
        .attr("height", "130%")
        .attr("width", "180%");


      filter.append("feGaussianBlur")
        .attr("in", "SourceAlpha")
        .attr("stdDeviation", 1.4)
        .attr("result", "blur");

      filter.append("feOffset")
        .attr("in", "blur")
        .attr("dx", 2.5)
        .attr("dy", 2.5)
        .attr("result", "offsetBlur");

      var feMerge = filter.append("feMerge");

      feMerge.append("feMergeNode")
        .attr("in", "offsetBlur")
      feMerge.append("feMergeNode")
        .attr("in", "SourceGraphic");

    //Drop shadow for hover end----------------------

      gEnter.append("rect").style("opacity",0);
      gEnter.append('g').attr('class', 'nv-x nv-axis');
      gEnter.append('g').attr('class', 'nv-y nv-axis');
      gEnter.append('g').attr('class', 'nv-stackedWrap');
      d3.select('#legend_svg').append('g').attr('class', 'nv-legendWrap');
      gEnter.append('g').attr('class', 'nv-controlsWrap');
      gEnter.append('g').attr('class', 'nv-interactive');

      g.select("rect").attr("width", availableWidth).attr("height",availableHeight);

      //------------------------------------------------------------
      // Legend

    function getObjects(obj, key, val) {
        var objects = [];
        for (var i in obj) {
            if (!obj.hasOwnProperty(i)) continue;
            if (typeof obj[i] == 'object') {
            objects = objects.concat(getObjects(obj[i], key, val));
        } else if (i == key && obj[key] == val) {
            objects.push(obj);
        }
    }
        return objects;
    }

    function reload (){
        d3.selectAll('#chart1')
            .datum(histcatexplong)
            .transition().duration(transitionDuration)
            .call(chart);
        //d3.selectAll('.horizontalGrid').remove();
        //var update = setInterval(grid_set, 1300);
        //clearInterval(update);
        //setTimeout(grid_set, 1300);
    }

      if (showLegend) {
        var legendWidth = (showControls) ? availableWidth - controlWidth : availableWidth;
        legend
          //.width(legendWidth);
          .width(100);

        d3.select('.nv-legendWrap')
            .datum(data)
            .call(legend);

        d3.select('.nv-legendWrap')
            //.attr('transform', 'translate(' + (availableWidth-legendWidth) + ',' + (-margin.top) +')');
            .attr('transform', 'translate(10, 2)');
      }
      var series_doubleclick = d3.selectAll('.nv-series');
      series_doubleclick
        .on('dblclick', function(d, i){
            data.forEach(function(series_doubleclick) {
                series_doubleclick.disabled = true;
                d.disabled = false;
                $('.nv-series').attr('data-toggled','off');
            });
            reload();
            dispatch.stateChange({
                disabled: data.map(function(d) { return !!d.disabled })
            });
            $(this).attr('data-toggled','on');
            //dispatch.legendDblclick(d,i);
            var elem = d3.select(this),
                text = elem.select("text"),
                textwidth = text.node().getBBox().width;
            elem.on('click', function(){
                data.forEach(function(d) {
                    d.disabled = false;
                });
                state.disabled = data.map(function(d) { return !!d.disabled });
                dispatch.stateChange(state);
                var legendkey = d.key,
                    object_found = getObjects(histcatexplong, 'key', legendkey),
                    index = object_found[0].seriesIndex;
                histcatexplong.splice(index, 1);
                d3.selectAll('.nv-series').remove();
                reload();
            });
            text.attr("class", "nv-legend-text remove-word");
            elem.select('.delete-word')
                .attr({"x": textwidth+30, "y": 15, "fill": "#ffffff"})
                .style("opacity", 1);
            elem.select('.text-bg')
                .attr({'width': textwidth+50, "height": "28", "x": -5, "y": -4, "rx": 3, "ry": 3})
                .style("opacity", 0.6);
          });

      //------------------------------------------------------------



      //------------------------------------------------------------

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
      if (rightAlignYAxis) {
          g.select(".nv-y.nv-axis")
              .attr("transform", "translate(" + availableWidth + ",0)");
      }

      //------------------------------------------------------------
      // Main Chart Component(s)

      //------------------------------------------------------------
      //Set up interactive layer
      if (useInteractiveGuideline) {
        interactiveLayer
           .width(availableWidth)
           .height(availableHeight)
           .margin({left: margin.left, top: margin.top})
           .svgContainer(container)
           .xScale(x);
        wrap.select(".nv-interactive").call(interactiveLayer);
      }

      stacked
        .width(availableWidth)
        .height(availableHeight);

      var stackedWrap = g.select('.nv-stackedWrap')
          .datum(data)

      stackedWrap.transition().call(stacked);

      //------------------------------------------------------------


      //------------------------------------------------------------
      // Setup Axes

      if (showXAxis) {
        xAxis
          .scale(x)
          .ticks( availableWidth / 100 )
          //.tickSize( -availableHeight, 0);

        g.select('.nv-x.nv-axis')
            .attr('transform', 'translate(0,' + availableHeight + ')');

        g.select('.nv-x.nv-axis')
          .transition().duration(0)
            .call(xAxis);
      }

      if (showYAxis) {
        yAxis
          .scale(y)
          .ticks(stacked.offset() == 'wiggle' ? 0 : availableHeight / 36)
          .tickSize(-availableWidth+2, 0)
          .setTickFormat( (stacked.style() == 'expand' || stacked.style() == 'stack_percent')
                ? d3.format('%') : yAxisTickFormat);

        g.select('.nv-y.nv-axis')
          .transition().duration(0)
            .call(yAxis);
      }

      //GRID FUNCTIONS-----------------------------------------

      function grid_set() {
        d3.selectAll('.horizontalGrid').remove();
        var grid_add = d3.select('.nv-y g g').selectAll('.tick'),
            grid =  container.select('.nv-y g g').selectAll('.tick')
                .filter(":nth-child(2n+1):not(:first-child)")
                .selectAll("line.horizontalGrid")
                .data(d3.range(1));
        grid.exit().remove();

        d3.selectAll('.tick').selectAll("line")
            .style("opacity", 0)

        d3.selectAll('.tick').selectAll("line")
            .transition()
            .duration(500)
            .style("stroke", "grey")
            .style("opacity", 0.6);

        grid
            .enter()
            .append("rect")
            .attr(
                {
                "class":"horizontalGrid",
                "fill" : "grey",
                "shape-rendering" : "crispEdges",
                "stroke" : "none",
                "width": availableWidth - 2,
                "height": "5px"
                })
            .style("opacity", 0.2)

        grid.exit().remove();

        var grid_height = Math.round((
            d3.transform(grid_add
                .filter(":nth-child(1)")
                .attr('transform')).translate[1]) -
            (d3.transform(grid_add
                .filter(":nth-child(2)")
                .attr('transform')).translate[1]));

        grid
            .transition()
            .duration(500)
            .attr(
                {
                "width": availableWidth - 2,
                "height": grid_height
                })
            .style("filter", "url(#drop-shadow)");
      }
setTimeout(grid_set, 300);
      //------------------------------------------------------------


      //============================================================
      // Event Handling/Dispatching (in chart's scope)
      //------------------------------------------------------------

      stacked.dispatch.on('areaClick.toggle', function(e) {
        if (data.filter(function(d) { return !d.disabled }).length === 1)
          data.forEach(function(d) {
            d.disabled = false;
          });
        else
          data.forEach(function(d,i) {
            d.disabled = (i != e.seriesIndex);
          });
        state.disabled = data.map(function(d) { return !!d.disabled });
        dispatch.stateChange(state);
        chart.update();
        d3.selectAll('.horizontalGrid').remove();
        var update = setInterval(grid_set, 300);
        clearInterval(update);
    });
      legend.dispatch.on('stateChange', function(newState) {
        state.disabled = newState.disabled;
        dispatch.stateChange(state);
        d3.selectAll('.horizontalGrid').remove();
        chart.update();
        var update = setInterval(grid_set, 300);
        clearInterval(update);
      });

      controls.dispatch.on('legendClick', function(d,i) {
        if (!d.disabled) return;

        controlsData = controlsData.map(function(s) {
          s.disabled = true;
          return s;
        });
        d.disabled = false;

        stacked.style(d.style);


        state.style = stacked.style();
        dispatch.stateChange(state);

        chart.update();
      });


      interactiveLayer.dispatch.on('elementMousemove', function(e) {
          stacked.clearHighlights();
          var singlePoint, pointIndex, pointXLocation, allData = [];
          data
          .filter(function(series, i) {
            series.seriesIndex = i;
            return !series.disabled;
          })
          .forEach(function(series,i) {
              pointIndex = nv.interactiveBisect(series.values, e.pointXValue, chart.x());
              stacked.highlightPoint(i, pointIndex, true);
              var point = series.values[pointIndex];
              if (typeof point === 'undefined') return;
              if (typeof singlePoint === 'undefined') singlePoint = point;
              if (typeof pointXLocation === 'undefined') pointXLocation = chart.xScale()(chart.x()(point,pointIndex));

              //If we are in 'expand' mode, use the stacked percent value instead of raw value.
              var tooltipValue = (stacked.style() == 'expand') ? point.display.y : chart.y()(point,pointIndex);
              allData.push({
                  key: series.key,
                  value: tooltipValue,
                  color: color(series,series.seriesIndex),
                  stackedValue: point.display
              });
          });

          allData.reverse();

          //Highlight the tooltip entry based on which stack the mouse is closest to.
          if (allData.length > 2) {
            var yValue = chart.yScale().invert(e.mouseY);
            var yDistMax = Infinity, indexToHighlight = null;
            allData.forEach(function(series,i) {

               //To handle situation where the stacked area chart is negative, we need to use absolute values
               //when checking if the mouse Y value is within the stack area.
               yValue = Math.abs(yValue);
               var stackedY0 = Math.abs(series.stackedValue.y0);
               var stackedY = Math.abs(series.stackedValue.y);
               if ( yValue >= stackedY0 && yValue <= (stackedY + stackedY0))
               {
                  indexToHighlight = i;
                  return;
               }
            });
            if (indexToHighlight != null)
               allData[indexToHighlight].highlight = true;
          }

          var xValue = xAxis.tickFormat()(chart.x()(singlePoint,pointIndex));

          //If we are in 'expand' mode, force the format to be a percentage.
          var valueFormatter = (stacked.style() == 'expand') ?
               function(d,i) {return d3.format(".1%")(d);} :
               function(d,i) {return yAxis.tickFormat()(d); };
          interactiveLayer.tooltip
                  .position({left: pointXLocation + margin.left, top: e.mouseY + margin.top})
                  .chartContainer(that.parentNode)
                  .enabled(tooltips)
                  .valueFormatter(valueFormatter)
                  .data(
                      {
                        value: xValue,
                        series: allData
                      }
                  )();

          interactiveLayer.renderGuideLine(pointXLocation);

      });

      interactiveLayer.dispatch.on("elementMouseout",function(e) {
          dispatch.tooltipHide();
          stacked.clearHighlights();
      });


      dispatch.on('tooltipShow', function(e) {
        if (tooltips) showTooltip(e, that.parentNode);
      });

      // Update chart from a state object passed to event handler
      dispatch.on('changeState', function(e) {

        if (typeof e.disabled !== 'undefined' && data.length === e.disabled.length) {
          data.forEach(function(series,i) {
            series.disabled = e.disabled[i];
          });

          state.disabled = e.disabled;
        }

        if (typeof e.style !== 'undefined') {
          stacked.style(e.style);
        }

        chart.update();
      });

    });
    return chart;
  }


  //============================================================
  // Event Handling/Dispatching (out of chart's scope)
  //------------------------------------------------------------

  stacked.dispatch.on('tooltipShow', function(e) {
    //disable tooltips when value ~= 0
    //// TODO: consider removing points from voronoi that have 0 value instead of this hack
    /*if (!Math.round(stacked.y()(e.point) *100)) {  // 100 will not be good for very small numbers... will have to think about making this valu dynamic, based on data range
      setTimeout(function() { d3.selectAll('.point.hover').classed('hover', false) }, 0);
      return false;
    }*/

    e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top],
    dispatch.tooltipShow(e);
  });

  stacked.dispatch.on('tooltipHide', function(e) {
    dispatch.tooltipHide(e);
  });

  dispatch.on('tooltipHide', function() {
    if (tooltips) nv.tooltip.cleanup();
  });

  //============================================================


  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  // expose chart's sub-components
  chart.dispatch = dispatch;
  chart.stacked = stacked;
  chart.legend = legend;
  chart.controls = controls;
  chart.xAxis = xAxis;
  chart.yAxis = yAxis;
  chart.interactiveLayer = interactiveLayer;

  d3.rebind(chart, stacked, 'x', 'y', 'size', 'xScale', 'yScale', 'xDomain', 'yDomain', 'xRange', 'yRange', 'sizeDomain', 'interactive', 'useVoronoi', 'offset', 'order', 'style', 'clipEdge', 'forceX', 'forceY', 'forceSize', 'interpolate');

  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
    margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = nv.utils.getColor(_);
    legend.color(color);
    stacked.color(color);
    return chart;
  };

  chart.showControls = function(_) {
    if (!arguments.length) return showControls;
    showControls = _;
    return chart;
  };

  chart.showLegend = function(_) {
    if (!arguments.length) return showLegend;
    showLegend = _;
    return chart;
  };

  chart.showXAxis = function(_) {
    if (!arguments.length) return showXAxis;
    showXAxis = _;
    return chart;
  };

  chart.showYAxis = function(_) {
    if (!arguments.length) return showYAxis;
    showYAxis = _;
    return chart;
  };

  chart.rightAlignYAxis = function(_) {
    if(!arguments.length) return rightAlignYAxis;
    rightAlignYAxis = _;
    yAxis.orient( (_) ? 'right' : 'left');
    return chart;
  };

  chart.useInteractiveGuideline = function(_) {
    if(!arguments.length) return useInteractiveGuideline;
    useInteractiveGuideline = _;
    if (_ === true) {
       chart.interactive(false);
       chart.useVoronoi(false);
    }
    return chart;
  };

  chart.tooltip = function(_) {
    if (!arguments.length) return tooltip;
    tooltip = _;
    return chart;
  };

  chart.tooltips = function(_) {
    if (!arguments.length) return tooltips;
    tooltips = _;
    return chart;
  };

  chart.tooltipContent = function(_) {
    if (!arguments.length) return tooltip;
    tooltip = _;
    return chart;
  };

  chart.state = function(_) {
    if (!arguments.length) return state;
    state = _;
    return chart;
  };

  chart.defaultState = function(_) {
    if (!arguments.length) return defaultState;
    defaultState = _;
    return chart;
  };

  chart.noData = function(_) {
    if (!arguments.length) return noData;
    noData = _;
    return chart;
  };

  chart.transitionDuration = function(_) {
    if (!arguments.length) return transitionDuration;
    transitionDuration = _;
    return chart;
  };

  chart.controlsData = function(_) {
    if (!arguments.length) return cData;
    cData = _;
    return chart;
  };

  chart.controlLabels = function(_) {
    if (!arguments.length) return controlLabels;
    if (typeof _ !== 'object') return controlLabels;
    controlLabels = _;
    return chart;
  };

  yAxis.setTickFormat = yAxis.tickFormat;

  yAxis.tickFormat = function(_) {
    if (!arguments.length) return yAxisTickFormat;
    yAxisTickFormat = _;
    return yAxis;
  };


  //============================================================

  return chart;
}