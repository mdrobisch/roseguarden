RoseGuardenApp.controller('AdminDoorsCtrl', function($scope,$q, Door) {

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
            local: 0 };

    $scope.rowCollection = [];
    $scope.displayedCollection = [];

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

    $scope.addDoorItem = function addDoorItem() {
        $scope.rowCollection.push({
            id: id,
            name: $scope.newdoor.name,
            doorSlot: $scope.newdoor.doorSlot,
            address: $scope.newdoor.address,
            local: 0 });
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