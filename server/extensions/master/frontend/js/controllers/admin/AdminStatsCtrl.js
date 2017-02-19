/**
 * Created by drobisch on 20.10.15.
 */

RoseGuardenApp.controller('AdminStatsCtrl', function($scope, $log, $q, Statistic) {

    $scope.isLoading = true;
    $scope.isLoadingData = false;
    $scope.showError = false;
    $scope.showInfo = false;
    $scope.statsAvailable = false;

    //$scope.labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    //$scope.data = [10, 10, 10, 10, 10, 20, 20];

    $scope.today = function() {
        $scope.dt = new Date();
    };

    $scope.today();

    $scope.clear = function () {
        $scope.dt = null;
    };

    // Disable weekend selection
    $scope.disabled = function(date, mode) {
        return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
    };

    $scope.toggleMin = function() {
        $scope.minDate = $scope.minDate ? null : new Date();
    };

    $scope.toggleMin();

    $scope.open = function($event) {
        $event.preventDefault();
        $event.stopPropagation();

        $scope.opened = true;
    };


    $scope.initDate = new Date('2016-01-01');
    $scope.formats = ['yyyy','dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
    $scope.format = $scope.formats[0];

    $scope.datepickerOptions = {
        datepickerMode:"'year'",
        minMode:"'year'",
        minDate:"minDate",
        showWeeks:"false",
    };

    $scope.currentPage = 0;
    $scope.statCollection = [];

    $scope.statType = 'Line';
    $scope.maxSize = 5;
    $scope.showYearPicker = false;

    function loadItemsFromAPI() {

        $scope.isLoading = true;
        deferred = $q.defer();
        Statistic.getList(true).then(function(data) {
            if(data.length > 0) {
                for (i = 0; i < data.length; i++) {
                    $scope.statCollection.push(data[i]);
                }
                $scope.statsAvailable = true;
                $scope.totalStats = data.length;
                $scope.currentPage = 1;
                $scope.pageChanged();
            } else {
                $scope.statsAvailable = false;
                $scope.showInfo = true;
                $scope.info = "No statistics available. \n Please check the STATISTICS_ENABLE in your config.";
            }

            $scope.isLoading = false;

            return deferred.resolve();
        }, function(response) {
            $scope.showError = false;
            return deferred.reject(response);
        });
        return deferred.promise
    }

    $scope.$watch("dt", function(newValue, oldValue) {
        console.log("I've changed : ", $scope.dt);
        if($scope.statCollection != null)
            $scope.pageChanged();
    });

    var $chart;
    $scope.$on("create", function (event, chart) {
      if (typeof $chart !== "undefined") {
        $chart.destroy();
      }

      $chart = chart;
    });

    function getSeriesNameByIndex(seriesIndex, selectedStat) {
        var seriesName = "";
        switch (seriesIndex) {
            case 0:
                seriesName = selectedStat.seriesName1;
                break;
            case 1:
                seriesName = selectedStat.seriesName2;
                break;
            case 2:
                seriesName = selectedStat.seriesName3;
                break;
            case 3:
                seriesName = selectedStat.seriesName4;
                break;
            case 4:
                seriesName = selectedStat.seriesName5;
                break;
            case 5:
                seriesName = selectedStat.seriesName6;
                break;
            case 6:
                seriesName = selectedStat.seriesName7;
                break;
            case 7:
                seriesName = selectedStat.seriesName8;
                break;
            default:
                seriesName = "Invalid";
                break;
        }
        return seriesName;
    }

    $scope.updateChart = function(statIndex, data) {
        var selectedStat = $scope.statCollection[statIndex];

        var STATDISPLAY_CONFIG_SHOW_DESCRIPTION = 1
        var STATDISPLAY_CONFIG_NO_TOTAL = 2

        switch (selectedStat.statType) {
            case 1: /* STATTYPE_LINE_SERIES */
            case 8:

                switch (selectedStat.statType) {
                    case 8:
                        $scope.statType = 'Bar';
                        break;
                    default:
                        $scope.statType = 'Line';
                        break;
                }

                console.log("Line " + selectedStat.statType + " " + $scope.dt.getYear());
                console.log(selectedStat);
                console.log(data[0]);

                $scope.statData = [];
                $scope.statSeries = [];
                $scope.statLabels = []
                $scope.showYearPicker = true;

                for(var i = 1; i <= 12;i++)
                    $scope.statLabels.push( i + "/" + ($scope.dt.getFullYear() % 1000));

                displayedSeries = selectedStat.seriesCount;
                if (selectedStat.seriesCount > 1  && (selectedStat.displayConfig & STATDISPLAY_CONFIG_NO_TOTAL) == 0)
                    displayedSeries ++;

                for(var i=0;i<displayedSeries;i++){
                    var seriesName = "";
                    var seriesIndex = i;

                    if (selectedStat.seriesCount > 1 && (selectedStat.displayConfig & STATDISPLAY_CONFIG_NO_TOTAL) == 0)
                        seriesIndex--;

                    console.log( (selectedStat.displayConfig & STATDISPLAY_CONFIG_NO_TOTAL))

                    if(i == 0) {
                        if (selectedStat.seriesCount > 1 && (selectedStat.displayConfig & STATDISPLAY_CONFIG_NO_TOTAL) == 0)
                            seriesName = "Total";
                        else
                            seriesName = getSeriesNameByIndex(0,selectedStat);
                    }
                    else {
                        seriesName = getSeriesNameByIndex(seriesIndex,selectedStat);
                    }
                    $scope.statSeries.push(seriesName);
                    newSeries = [];
                    for( var j = 0; j< 12;j++)
                        newSeries.push(null);
                    $scope.statData.push(newSeries);
                }

                for (var i = 0;i < data.length;i++) {
                    if(data[i].year == $scope.dt.getFullYear()) {
                        if (selectedStat.seriesCount > 1  && (selectedStat.displayConfig & STATDISPLAY_CONFIG_NO_TOTAL) == 0) {
                            $scope.statData[data[i].series+1][data[i].month - 1] = parseFloat(data[i].value);
                            if($scope.statData[0][data[i].month - 1] == null)
                                $scope.statData[0][data[i].month - 1] = parseFloat(data[i].value);
                            else
                                $scope.statData[0][data[i].month - 1] += parseFloat(data[i].value);
                        }
                        else {
                            $scope.statData[data[i].series][data[i].month - 1] = parseFloat(data[i].value);
                        }
                    }
                }
                break;
            case 2: /* STATTYPE_BAR_SERIES */
                console.log("Bar " + selectedStat.statType);
                console.log(data.length + " " + data[0]);
                $scope.statLabels = ["Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15", "Jan. 15"];
                $scope.statData = [[65, 0, 80, 81, 56, null , 40, 10, 100, 2]];
                $scope.statSeries = ['Series A'];
                $scope.statType = 'Bar';
                $scope.showYearPicker = true;
                break;
            case 3: /* STATTYPE_RADAR_CLASSES */
                console.log("Radar " + selectedStat.statType);
                console.log(data.length  + " " + data[0]);
                $scope.statData = [];
                $scope.statSeries = [];
                $scope.statLabels = [];
                $scope.statSeries = [];
                $scope.showYearPicker = true;

                for(var s = 0; s < selectedStat.seriesCount;s++ ) {
                    newSeries = [];
                    for (var i = 0;i < selectedStat.binningCount;i++) {
                        $scope.statLabels.push(null);
                        newSeries.push(data[i].value);
                    }
                    $scope.statData.push(newSeries);
                    $scope.statSeries.push(getSeriesNameByIndex(s,selectedStat));
                }

                for (var i = 0;i < data.length;i++) {
                    if(data[i].series == 0)
                        $scope.statLabels[data[i].binningId] = data[i].label;
                    $scope.statData[data[i].series][data[i].binningId] = data[i].value;
                }
                // $scope.statSeries.push("Weekdays ");

                $scope.statType = 'Radar';
                $scope.showYearPicker = false;
                break;
            case 5: /* STATTYPE_DOUGHNUT_CLASSES */
                console.log("Doughnut " + selectedStat.statType);
                $scope.statSeries = [];
                $scope.statLabels = [];
                $scope.statData = [];

                for (var i = 0;i < data.length;i++) {
                    $scope.statLabels.push(data[i].label)
                    $scope.statData.push(data[i].value)
                }

                for( var i = 0; i< 5;i++)
                    $scope.statData.push(Math.round(Math.random()*10));
                //[10, 10, 12, 10, 11, 20, 20, 10, 10, 10, 10, 10];
                $scope.statType = 'Doughnut';
                $scope.showYearPicker = false;
                break;
        }
    };


    $scope.pageChanged = function() {
        var statIndex = $scope.currentPage - 1;
        var selectedStat = $scope.statCollection[statIndex];
        if(selectedStat == undefined)
            return;

        $log.log('Page changed to: ' + $scope.currentPage);
        console.log(selectedStat);
        $scope.statTitle = selectedStat.name;
        $scope.isLoadingData = true;

        deferred = $q.defer();
        Statistic.getEntryList(selectedStat.id).then(function(data) {
            $scope.isLoadingData = false;
            console.log("Entrylist:" + data.length)
            $scope.updateChart (statIndex, data);
            return deferred.resolve();
        }, function(response) {
            $scope.showError = false;
            $scope.isLoadingData = false;
            return deferred.reject(response);
        });
        return deferred.promise;
    };

    loadItemsFromAPI();

});
