$(function () {
    $('#hiringchart').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: '錄取率'
        },
        subtitle: {
            text: ''
        },
        xAxis: {
            categories: [
                '',
                
            ],
            crosshair: true
        },
        yAxis: {
            min: 0,
            max: 1,
            title: {
                text: ''
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        exporting: {
         enabled: false
        },
        series: [{
            name: 'Green',
            data: [{{ green_hiring_rate }}],
            color: 'green'

        }, {
            name: 'Purple',
            data: [{{ purple_hiring_rate }}],
            color: 'purple'

        }]
    });
});