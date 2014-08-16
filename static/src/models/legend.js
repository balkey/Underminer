nv.models.legend = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var margin = {top: 0, right: 0, bottom: 0, left: 0}
    , width = null
    , height = null
    , getKey = function(d) { return d.key }
    , color = nv.utils.defaultColor()
    , align = false
    //, rightAlign = true
    , rightAlign = false
    , updateState = true   //If true, legend will update data.disabled and trigger a 'stateChange' dispatch.
    , radioButtonMode = false   //If true, clicking legend items will cause it to behave like a radio button. (only one can be selected at a time)
    , dispatch = d3.dispatch('legendClick', 'legendDblclick', 'legendMouseover', 'legendMouseout', 'stateChange')
    ;

  //============================================================


  function chart(selection) {
    selection.each(function(data) {
      var availableWidth = width - margin.left - margin.right,
          container = d3.select(this);


      //------------------------------------------------------------
      // Setup containers and skeleton of chart
      var chart = d3.select('.nv-legendWrap');
      var wrap = chart.selectAll('g.nv-legend').data([data]);
      var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-legend').append('g');
      var g = wrap.select('g')

      wrap.attr('transform', 'translate(0, -13)');

      //------------------------------------------------------------

      var series = g.selectAll('.nv-series')
          .data(function(d) { return d });
      var seriesEnter = series.enter().append('g')
          .each(function(d,i) {d3.select(this).attr('index', i);})
          .attr('class', 'nv-series')
          .attr("transform", "translate(0, 21)")
          .attr('data-toggled', '')
          /*.on('mouseover', function(d,i) {
            dispatch.legendMouseover(d,i);  //TODO: Make consistent with other event objects
          })
          .on('mouseout', function(d,i) {
            dispatch.legendMouseout(d,i);
          })*/
          /*.on('dblclick', function(d, i){
            dispatch.legendDblclick(d,i);
            var elem = d3.select(this);
            var text = elem.select("text");
            var textwidth = text.node().getBBox().width;
            var legendkey = d.key;
            elem.on('click', function(){
                var object_found = getObjects(histcatexplong, 'key', legendkey);
                var index = object_found[0].seriesIndex;
                delete histcatexplong[index];
                after_delete();


                //alert(JSON.stringify(object_found));
            });
            //elem.attr("class","nv-series delete_state");
            text.attr("class", "nv-legend-text remove-word");
            elem.select('.delete-word')
                .attr({"x": textwidth+30, "y": 15, "fill": "#ffffff"})
                .style("opacity", 1);
            elem.select('.text-bg')
                .attr({'width': textwidth+50, "height": "28", "x": -5, "y": -4, "rx": 3, "ry": 3})
                .style("opacity", 0.6);
          })*/
          /*.on('mouseout', function(d, i){
            //dispatch.legendDblclick(d,i);
            var elem = d3.select(this);
            var text = elem.select("text");
            var textwidth = text.node().getBBox().width;
            setTimeout(function(){
                text.attr("class", "nv-legend-text");
                elem.select('.text-bg').style("opacity", 0);
            }, 2000)
          })*/
          /*.on('mouseover', function(d, i){
            var elem = d3.select.this;
            elem.on('dblclick');
            })*/





          /*.on('dbclick', function(d,i) {
            dispatch.legendClick(d,i);
            if (updateState) {
               if (radioButtonMode) {
                   //Radio button mode: set every series to disabled,
                   //  and enable the clicked series.
                   data.forEach(function(series) { series.disabled = true});
                   d.disabled = false;
               }
               else {
                   d.disabled = !d.disabled;
                   if (data.every(function(series) { return series.disabled})) {
                       //the default behavior of NVD3 legends is, if every single series
                       // is disabled, turn all series' back on.
                       data.forEach(function(series) { series.disabled = false});
                   }
               }
               dispatch.stateChange({
                  disabled: data.map(function(d) { return !!d.disabled })
               });
            }
          })*/
          .on('click', function(d,i) {
            if (!$(this).attr('data-toggled') || $(this).attr('data-toggled') == 'off'){
                dispatch.legendClick(d,i);
                if (updateState) {
                    data.forEach(function(series) {
                        series.disabled = true;
                        $('.nv-series').attr('data-toggled','off');
                    });
                    d.disabled = false;
                    dispatch.stateChange({
                        disabled: data.map(function(d) { return !!d.disabled })
                    });
                }
                $(this).attr('data-toggled','on');
            }
            else if ($(this).attr('data-toggled') == 'on'){
                    dispatch.legendClick(d,i);
                    if (updateState) {
                        data.forEach(function(series) {
                            series.disabled = false;
                            $('.nv-series').attr('data-toggled','');

                        });
                        d.disabled = false;
                        dispatch.stateChange({
                            disabled: data.map(function(d) { return !!d.disabled })
                        });
                    }
                $(this).attr('data-toggled','off');
            }

          });


      seriesEnter.append('rect')
          .style('stroke-width', 2)
          .attr('class','nv-legend-symbol')
          .attr('height', 20)
          .attr('width', 20);

      seriesEnter.append('rect')
          .style({"stroke-width": "1", "stroke": "#000000", "fill": "none", "opacity": .4})
          .attr('class','nv-legend-symbol')
          .attr('height', 22)
          .attr('width', 22)
          .attr('x', -1)
          .attr('y', -1);

      seriesEnter.append('text')
          .attr('text-anchor', 'start')
          .attr('class','nv-legend-text')
          .attr('dy', '1em')
          .attr('dx', '25');

      seriesEnter.insert('rect', ':first-child')
        .attr('class', 'text-bg')
            .style({"opacity": 0, "fill": "#ea202d"});

      seriesEnter.append('text')
            .text("X")
            .attr("class", "delete-word")
            .style("opacity", 0);

    seriesEnter
        .on('mouseleave', function(){
            d3.select(this).select('.delete-word').style("opacity", 0);
            d3.select(this).select('.text-bg').style("opacity", 0);
            d3.select(this).select('.nv-legend-text').attr("class", "nv-legend-text");
            d3.select(this).on("click", function(d,i) {
            if (!$(this).attr('data-toggled') || $(this).attr('data-toggled') == 'off'){
                dispatch.legendClick(d,i);
                if (updateState) {
                    data.forEach(function(series) {
                        series.disabled = true;
                        $('.nv-series').attr('data-toggled','off');
                    });
                    d.disabled = false;
                    dispatch.stateChange({
                        disabled: data.map(function(d) { return !!d.disabled })
                    });
                }
                $(this).attr('data-toggled','on');
            }
            else if ($(this).attr('data-toggled') == 'on'){
                    dispatch.legendClick(d,i);
                    if (updateState) {
                        data.forEach(function(series) {
                            series.disabled = false;
                            $('.nv-series').attr('data-toggled','');

                        });
                        d.disabled = false;
                        dispatch.stateChange({
                            disabled: data.map(function(d) { return !!d.disabled })
                        });
                    }
                $(this).attr('data-toggled','off');
            }

          });
        });

      series.classed('disabled', function(d) { return d.disabled });
      series.exit().remove();
      series.select('.nv-legend-symbol')
          .style('fill', function(d,i) { return d.color || color(d,i)})
          .style('stroke', function(d,i) { return d.color || color(d, i) });
      series.select('text').text(getKey);

//TODO: implement fixed-width and max-width options (max-width is especially useful with the align option)

      // NEW ALIGNING CODE, TODO: clean up
     if (align) {

        var seriesWidths = [];
        series.each(function(d,i) {
              var legendText = d3.select(this).select('text');
              var nodeTextLength;
              try {
                nodeTextLength = legendText.node().getComputedTextLength();
                // If the legendText is display:none'd (nodeTextLength == 0), simulate an error so we approximate, instead
                if(nodeTextLength <= 0) throw Error();
              }
              catch(e) {
                nodeTextLength = nv.utils.calcApproxTextWidth(legendText);
              }

              seriesWidths.push(nodeTextLength + 28); // 28 is ~ the width of the circle plus some padding
            });


        var seriesPerRow = 0;
        var legendWidth = 0;
        var columnWidths = [];

        while ( legendWidth < availableWidth && seriesPerRow < seriesWidths.length) {
          columnWidths[seriesPerRow] = seriesWidths[seriesPerRow];
          legendWidth += seriesWidths[seriesPerRow++];
        }
        if (seriesPerRow === 0) seriesPerRow = 2; //minimum of one series per row


        while ( legendWidth > availableWidth && seriesPerRow > 1 ) {
          columnWidths = [];
          seriesPerRow--;

          for (var k = 0; k < seriesWidths.length; k++) {
            if (seriesWidths[k] > (columnWidths[k % seriesPerRow] || 0) )
              columnWidths[k % seriesPerRow] = seriesWidths[k];
          }

          legendWidth = columnWidths.reduce(function(prev, cur, index, array) {
                          return prev + cur;
                        });
        }

        var xPositions = [];
        for (var i = 0, curX = 0; i < seriesPerRow; i++) {
            xPositions[i] = curX;
            curX += columnWidths[i];
        }

        series
            .attr('transform', function(d, i) {
              return 'translate(' + xPositions[i % seriesPerRow] + ',' + (5 + Math.floor(i / seriesPerRow) * 20) + ')';
            });

        //position legend as far right as possible within the total width
        if (rightAlign) {
           g.attr('transform', 'translate(' + (width - margin.right - legendWidth) + ',' + margin.top + ')');
        }
        else {
           g.attr('transform', 'translate(0' + ',' + margin.top + ')');
        }

        height = margin.top + margin.bottom + (Math.ceil(seriesWidths.length / seriesPerRow) * 20);

      } else {

        var ypos = 15,
            newxpos = 5,
            maxwidth = 0,
            xpos;
        series
            .attr('transform', function(d, i) {
              var length = d3.select(this).select('text').node().getComputedTextLength() + 28;
              xpos = newxpos;

              if (width < margin.left + margin.right + xpos + length) {
                newxpos = xpos = 5;
                ypos += 17;
              }

              newxpos += length;
              if (newxpos > maxwidth) maxwidth = newxpos;

              return 'translate(0 ,' + ypos + ')';

            });

        //position legend as far right as possible within the total width
        g.attr('transform', 'translate(0, ' + margin.top + ')');

        height = margin.top + margin.bottom + ypos + 15;

      }

    });
    d3.selectAll('.nv-series').each(function() {
            if (Number(d3.select(this).attr('index'))%2 !== 0) {
                var y_pos = d3.transform(d3.select(this).attr('transform')).translate[1];
                d3.select(this).attr('transform', "translate(125," + (y_pos-17) +')');
            }
            else {
                var y_pos = d3.transform(d3.select(this).attr('transform')).translate[1];
                d3.select(this).attr('transform', "translate(0," + y_pos +')');
            }
            });

    return chart;
  }

  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  chart.dispatch = dispatch;
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

  chart.key = function(_) {
    if (!arguments.length) return getKey;
    getKey = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = nv.utils.getColor(_);
    return chart;
  };

  chart.align = function(_) {
    if (!arguments.length) return align;
    align = _;
    return chart;
  };

  chart.rightAlign = function(_) {
    if (!arguments.length) return rightAlign;
    rightAlign = _;
    return chart;
  };

  chart.updateState = function(_) {
    if (!arguments.length) return updateState;
    updateState = _;
    return chart;
  };

  chart.radioButtonMode = function(_) {
    if (!arguments.length) return radioButtonMode;
    radioButtonMode = _;
    return chart;
  };

  //============================================================


  return chart;
}