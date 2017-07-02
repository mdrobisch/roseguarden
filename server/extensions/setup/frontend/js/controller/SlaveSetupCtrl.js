RoseGuardenApp.controller('SlaveSetupCtrl', function($scope, $q, Setup, $route, $window, $location,$timeout, $interval) {

    var i=0;
    i++;
    $scope.isLoading = true;
    $scope.isStatusRequestPending = false;
    $scope.isStarted = false;
    $scope.isFinished = false;
    $scope.isFailed = false;
    $scope.setupStatus = "Not started";
    $scope.setupBarColor = "";
    $scope.setupProgress = 100;
    $scope.isLockPending = false;


    $scope.logs = [];

    $scope.startSetup = function () {
        deferred = $q.defer();
        Setup.start(null, true).then(function (status) {
            $scope.isStarted = true;
            $scope.setupStatus = "Started";
            $scope.setupBarColor = "warning";
            $scope.isFinished = false;
            $scope.logs = [
                {date :  moment().format("YYYY-MM-DD HH:mm:ss"), log : "Setup request sent to client ..."}
            ];

            return deferred.resolve(status);
        }, function(response) {
            console.log("rejected");
            $scope.isStatusRequestPending = false;
            return deferred.reject(response);
        });
        return deferred.promise
    };

    $scope.finishSetup = function () {
        deferred = $q.defer();
        Setup.lock(null, true).then(function (status) {
            console.log("locked");
            $timeout( function(){$window.location.reload(true); }, 2000);
            return deferred.resolve(status);
        }, function(response) {
            console.log("rejected");
            $scope.isStatusRequestPending = false;
            return deferred.reject(response);
        });
        return deferred.promise
    };

    $scope.pollStatus = function(credentials) {
        var me = this;
        deferred = $q.defer();
        Setup.getStatus(credentials, true).then(function(status) {
            if(typeof(status) === 'object')
                currentStatus = status;
            else
                currentStatus = JSON.parse(status);
            console.log(currentStatus);
            if (status.statusupdate == true) {
                console.log("new status");
                $scope.logs.unshift({date: moment(status.date).format("YYYY-MM-DD HH:mm:ss"), log: status.message});
                $scope.$broadcast('rebuild:statusbar');
                console.log(status.progress);
                if (status.progress < 100) {
                    $scope.setupStatus = "" + status.progress + "%";
                    $scope.setupProgress = status.progress;
                }
                else {
                    console.log("finished");
                    $scope.setupStatus = "Finished";
                    $scope.setupBarColor = "success";
                    $scope.isFinished = true;
                    $scope.setupProgress = 100;
                }
            }

            $scope.isStatusRequestPending = false;
            return deferred.resolve(status);
        }, function(response) {
            console.log("rejected");
            $scope.isStatusRequestPending = false;
            return deferred.reject(response);
        });
        return deferred.promise
    };


    $scope.getStatus = function() {
        if($scope.isStatusRequestPending == false) {
            if($scope.isStarted == true) {
                if($scope.isFinished == false) {
                    $scope.isStatusRequestPending = true;
                    this.pollStatus(null);
                }
            }
        }
    };

    $interval( function(){ $scope.getStatus(); }, 1000);

});