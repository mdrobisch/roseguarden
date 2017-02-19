RoseGuardenApp.controller('AdminDebugCtrl', function($scope, $q, Log) {

    var dates = [new Date("25 Dec, 1995 23:15:00"),new Date("1 Jan, 2005 13:15:00")];
    var nodeNames = ['Front door', 'ProtosV2'];
    var logtexts = ['Opening door','Unlock device'];
    var usernames = ['Marcus Drobisch', 'Max Mustermann'];
    var usermails = ['m.drobisch@googlemail.com', 'Max.Mustermann@googlemail.com'];
    var authentificationTypes = [0, 1,0, 0];
    var logTypes = [0, 1,0, 0];
    var logLevels = ['L1', 'L2', 'L3', 'L4'];

    var id = 1;

    $scope.rowCollection = [];
    $scope.displayedCollection = [];

    function generateRandomItem(id) {

        var date = dates[Math.floor(Math.random() * 2)];
        var nodeName = nodeNames[Math.floor(Math.random() * 2)];
        var logText = logtexts[Math.floor(Math.random() * 2)];
        var username = usernames[Math.floor(Math.random() * 2)];
        var usermail = usermails[Math.floor(Math.random() * 2)];
        var authentificationType = authentificationTypes[Math.floor(Math.random() * 2)];
        var logLevel = logLevels[Math.floor(Math.random() * 3)];
        var logType = logTypes[Math.floor(Math.random() * 3)];
        return {
            id: id,
            date: date,
            nodeName: nodeName,
            userName: username,
            userMail: usermail,
            authType: authentificationType,
            logText: logText,
            logType: logType,
            logLevel: logLevel
        };
    }

    function loadItemsDummy() {
        for (id; id < 19; id++) {
            $scope.rowCollection.push(generateRandomItem(id));
        }
        //copy the references (you could clone ie angular.copy but then have to go through a dirty checking for the matches)
        $scope.displayedCollection = [].concat($scope.rowCollection);
    }

    function loadItemsFromAPI() {

        $scope.isLoading = true;
        deferred = $q.defer();
        Log.getDebugLog(true).then(function(data) {
              console.log(data.length)
              for(i=0;i < data.length;i++) {
                  $scope.rowCollection.push(data[i]);
              }
            $scope.displayedCollection = [].concat($scope.rowCollection);
            $scope.isLoading = false;
            return deferred.resolve();
        }, function(response) {
            $scope.showError = false;
            return deferred.reject(response);
        });
        return deferred.promise
    }

    //loadItemsDummy();
    loadItemsFromAPI();

    //add to the real data holder
    $scope.addRandomItem = function addRandomItem() {
        $scope.rowCollection.push(generateRandomItem(id));
        id++;
    };

    //remove to the real data holder
    $scope.removeItem = function removeItem(row) {
        var index = $scope.rowCollection.indexOf(row);
        if (index !== -1) {
            $scope.rowCollection.splice(index, 1);
        }
    }
})