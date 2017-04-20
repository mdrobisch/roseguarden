RoseGuardenApp.controller('MasterSetupCtrl', function($scope, $q, Setup, $location, $interval) {

    var i=0;
    i++;
    $scope.isLoading = true;
    $scope.isStatusRequestPending = false;
    $scope.isStarted = false;
    $scope.isFinished = false;
    $scope.setupStatus = "Not started";
    $scope.setupBarColor = "";
    $scope.setupProgress = 100;
    $scope.isLockPending = false;


    $scope.logs = [
        {date : "2016", log : "Log"},
        {date : "2016", log : "Log2"}
    ];

    $scope.startSetup = function () {
        $scope.isStarted = true;
        $scope.setupStatus = "Started";
        $scope.setupBarColor = "warning";


    };

    $scope.finishSetup = function () {
        console.log("Test");
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
            console.log("got it");
            $scope.isStatusRequestPending = false;
            $scope.logs.unshift({date : moment(status.date).format("YYYY-MM-DD HH:mm:ss"), log : "Log"});
            $scope.$broadcast('rebuild:statusbar');
            if(status.progress < 100){
                $scope.setupStatus = "" + status.progress + "%";
                $scope.setupProgress = status.progress;
            }
            else {
                $scope.setupStatus = "Finished"
                $scope.setupBarColor = "success";
                $scope.isFinished = true;
            }

            return deferred.resolve(status);
        }, function(response) {
            console.log("rejected");
            $scope.isStatusRequestPending = false;
            return deferred.reject(response);
        });
        return deferred.promise
    };


    $scope.getStatus = function() {
        console.log("$scope.callAtInterval - Interval occurred");
        if($scope.isStatusRequestPending == false) {
            if($scope.isStarted == true) {
                if($scope.isFinished == false) {
                    $scope.isStatusRequestPending = true;
                    this.pollStatus(null);
                }
            }
        }
    };

    $interval( function(){ $scope.getStatus(); }, 2000);

});