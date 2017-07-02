RoseGuardenApp.controller('SlaveConfigCtrl', function($scope, $q, Config, $location) {

    var i=0;
    i++;
    $scope.isLoading = true;
    
    this.loadConfig = function(credentials) {
        var me = this;
        deferred = $q.defer();
        Config.get(credentials, true).then(function(config) {
            currentConfig = JSON.parse(config);
            console.log("got it");
            return deferred.resolve(config);
        }, function(response) {
            console.log("rejected");
            return deferred.reject(response);
        });
        return deferred.promise
    };

    function findConfigEntryByName(config, name) {
      for(var section in config) {
          //console.log(section + name);
        if(typeof config[section] === 'object') {
            for (var i = 0; i < config[section].entries.length; i++) {
                if (config[section].entries[i].name == name)
                    return config[section].entries[i];
            }
        }
      }
    }

    //console.log(ConfigService.getConfig());

    this.loadConfig().then(function(config_unparsed) {
        console.log("loaded");
        config = JSON.parse(config_unparsed);
        console.log(config);

        $scope.nodeName = findConfigEntryByName(config, "NODE_NAME");
        $scope.nodePassword = findConfigEntryByName(config, "INITIAL_NODE_PASSWORD");
        $scope.nodeExtensionName = findConfigEntryByName(config, "EXTENSION_NAME");
        $scope.nodeExtensionName.value = "slave";
        $scope.nodeExtensionFrontendDisable = findConfigEntryByName(config, "EXTENSION_FRONTEND_DISABLE");
        $scope.nodeDebug = findConfigEntryByName(config, "DEBUG");

        $scope.nodeIsMaster = findConfigEntryByName(config, "NODE_IS_MASTER");
        $scope.nodeIsMaster.value = false;

        $scope.masterGlobalRfidKey = findConfigEntryByName(config, "RFID_GLOBAL_PASSWORD");
        $scope.masterStatisticEnable = findConfigEntryByName(config, "STATISTICS_ENABLE");
        $scope.masterCleanupEnable = findConfigEntryByName(config, "CLEANUP_EANBLE");
        $scope.masterCleanupThreshold = findConfigEntryByName(config, "CLEANUP_THRESHOLD");
        $scope.masterSyncCyclic = findConfigEntryByName(config, "NODE_SYNC_CYCLIC");
        $scope.masterSyncCycle = findConfigEntryByName(config, "NODE_SYNC_CYCLE");
        $scope.masterSyncOnStartup = findConfigEntryByName(config, "NODE_SYNC_ON_STARTUP");

        $scope.interfaceDoor = findConfigEntryByName(config, "NODE_DOOR_AVAILABLE");
        $scope.interfaceDoorOpeningTime = findConfigEntryByName(config, "DOOR_OPENING_TIME");

        $scope.interfaceDoorKeymask = findConfigEntryByName(config, "DOOR_KEYMASK");
        $scope.interfaceDoorKeymaskForm = [];
        validKeyMask = parseInt($scope.interfaceDoorKeymask.value);
        for(var i = 0;i < 8; i++) {
            if ( ((0x01 << i) & validKeyMask) != 0)
                $scope.interfaceDoorKeymaskForm.push(true);
            else
                $scope.interfaceDoorKeymaskForm.push(false);
        }


        $scope.isLoading = false;


    }, function(response) {

    });



    $scope.randmoizeGlobalKey = function() {
        var token = "";
        for(var j= 0;j < 6;j++) {
            for (var i = 0; i < 2; i++) {
                token += String.fromCharCode(Math.random() * 10 + 48);
            }
            if (j != 5)
                token += "-";
        }
        $scope.masterGlobalRfidKey.value = token;
    };

    function updateConfig(configUpdate) {
        var me = this;
        deferred = $q.defer();
        console.log("request");
        Config.update(configUpdate, true).then(function(config) {
            console.log("updated");
            return deferred.resolve(config);
        }, function(response) {
            console.log("rejected");
            return deferred.reject(response);
        });
        return deferred.promise
    }

    $scope.saveConfig = function () {
        console.log($scope.interfaceDoorKeymask.value);
        $scope.interfaceDoorKeymask.value = 0;
        console.log($scope.interfaceDoorKeymask.value);
        for(var i = 0;i < 8; i++) {
            if($scope.interfaceDoorKeymaskForm[i] == true)
                $scope.interfaceDoorKeymask.value += Math.pow(2,i);
        }
        console.log($scope.interfaceDoorKeymask.value);

        updateConfig(config).then(function(config_unparsed) {
            $location.path("/slave/setup" );
        }, function(response) {
            console.log("rejected");

        });
    };

    $scope.log = function () {
        console.log(config.node_config.entries[0]);
    };

});