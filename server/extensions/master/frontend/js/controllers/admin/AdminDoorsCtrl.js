RoseGuardenApp.controller('AdminDoorsCtrl', function($scope,$q, Door, SyncRequest, $modal, $log) {

    var names = ['Front door', 'Back door'];
    var keyMasks = [0x01,-1];
    var addresses = ['192.168.2.10','192.168.8.1'];
    var locals = [0,0];

    var id = 1;

    $scope.newdoor = {
            id: 0,
            name: 'New door',
            doorSlot: 'Slot 1',
            address: '192.168.1.199',
            local: 0 ,
            password: ''};

    $scope.rowCollection = [];
    $scope.displayedCollection = [];

    $scope.requestSyncing = false;

    function generateRandomItem(id) {

        var name = names[Math.floor(Math.random() * 2)];
        var keyMask = keyMasks[Math.floor(Math.random() * 2)];
        var address = addresses[Math.floor(Math.random() * 2)];
        var local = locals[Math.floor(Math.random() * 2)];

        return {
            id: id,
            name: name,
            keyMask: keyMask,
            address: address,
            local: local
        };
    }

    function loadItemsDummy() {
        $scope.rowCollection.push({
            id: 0,
            name: 'Local door',
            keyMask: 0x03,
            address: 'http://localhost',
            local: 1 });

        for (id=1; id < 4; id++) {
            $scope.rowCollection.push(generateRandomItem(id));
        }
        //copy the references (you could clone ie angular.copy but then have to go through a dirty checking for the matches)
        $scope.displayedCollection = [].concat($scope.rowCollection);
    }


    function loadItemsFromAPI() {

        $scope.isLoading = true;
        deferred = $q.defer();
        Door.getList(true).then(function(doors) {
              for(i=0;i < doors.length;i++) {
                  $scope.rowCollection.push(doors[i]);
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

    loadItemsFromAPI();
    //loadItemsDummy();

    //add to the real data holder
    $scope.addRandomItem = function addRandomItem() {
        $scope.rowCollection.push(generateRandomItem(id));
        id++;
    };

    $scope.syncDoors = function syncDoors() {
        $scope.showError = false;
        $scope.requestSyncing = true;
        deferred = $q.defer();
        SyncRequest.create(true).then(function(response_data) {
            $log.info('Response  ' + response_data);

            $scope.dataLoading = false;
            $scope.showError = false;
            $scope.showSuccess = true;
            $scope.requestSyncing = false;

            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Request door sync failed' + ' (' + response.data + ' )'
            $scope.dataLoading = false;
            $scope.showSuccess = false;
            $scope.showError = true;
            $scope.requestSyncing = false;
            return deferred.reject(response);
        });
        return deferred.promise;
    };


    $scope.addDoor = function addDoor() {
        $scope.showError = false;
        deferred = $q.defer();
        var newdoor = {name:$scope.newdoor.name, address: $scope.newdoor.address, password: btoa($scope.newdoor.password)};

        Door.register(newdoor).then(function(response_data) {
            $log.info('Response  ' + response_data);

            $scope.dataLoading = false;
            $scope.showError = false;
            $scope.showSuccess = true;
            $scope.rowCollection.push(response_data);

            return deferred.resolve();
        }, function(response) {
            //$log.info('Response  ' + response);
            //console.log(response)
            $scope.error = 'Register new door failed' + ' (' + response.data + ' )'
            $scope.dataLoading = false;
            $scope.showSuccess = false;
            $scope.showError = true;
            return deferred.reject(response);
        });
        return deferred.promise
    };


    //remove to the real data holder
    $scope.synchronizeDoor = function synchronizeDoor(row) {
        console.log("synchronize door")
        var index = $scope.rowCollection.indexOf(row);
        if (index !== -1) {


            Door.delete(row.id).then(function() {
                $scope.profileUpdatePending = false;
                $scope.success = 'Door successfully removed.'
                $scope.showError = false;
                $scope.showSuccess = true;

                $scope.rowCollection.splice(index, 1);
                return deferred.resolve();
            }, function(response) {
                $scope.error = 'Removing door failed.'
                $scope.profileUpdatePending = false;
                $scope.showError = true;
                $scope.showSuccess = false;
                return deferred.reject(response);
            });
            return deferred.promise
        }

    };

    //remove to the real data holder
    $scope.removeDoor = function removeDoor(row) {

        var modalInstance = $modal.open({
          templateUrl: 'partials/modals/RemoveDoor.html',
          controller: 'RemoveUserCtrl',
          windowClass: 'center-modal',
          resolve: {
            name: function () {
                return row.name + ' from ' + row.address; }
          }
        });

        modalInstance.result.then(function (selected) {
            var index = $scope.rowCollection.indexOf(row);
            if (index !== -1) {


                Door.delete(row.id).then(function() {
                    $scope.profileUpdatePending = false;
                    $scope.success = 'Door successfully removed.'
                    $scope.showError = false;
                    $scope.showSuccess = true;

                    $scope.rowCollection.splice(index, 1);
                    return deferred.resolve();
                }, function(response) {
                    $scope.error = 'Removing door failed.'
                    $scope.profileUpdatePending = false;
                    $scope.showError = true;
                    $scope.showSuccess = false;
                    return deferred.reject(response);
                });
                return deferred.promise
            }

        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        });


    }
})