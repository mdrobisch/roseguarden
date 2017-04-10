RoseGuardenApp.controller('MasterConfigCtrl', function($scope, $q, Config, $location) {

    var i=0;
    i++;
    $scope.isLoading = true;
    
    this.loadConfig = function(credentials) {
        var me = this;
        deferred = $q.defer();
        Config.create(credentials, true).then(function(config) {
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
        $scope.nodePassword = findConfigEntryByName(config, "NODE_NAME");
        $scope.nodeExtensionName = findConfigEntryByName(config, "EXTENSION_NAME");
        $scope.nodeExtensionFrontendDisable = findConfigEntryByName(config, "EXTENSION_FRONTEND_DISABLE");
        $scope.nodeDebug = findConfigEntryByName(config, "DEBUG");

        $scope.nodeIsMaster = findConfigEntryByName(config, "NODE_IS_MASTER");
        $scope.nodeIsMaster.value = true;

        $scope.masterGlobalRfidKey = findConfigEntryByName(config, "RFID_GLOBAL_PASSWORD");
        $scope.masterStatisticEnable = findConfigEntryByName(config, "STATISTICS_ENABLE");
        $scope.masterCleanupEnable = findConfigEntryByName(config, "CLEANUP_EANBLE");
        $scope.masterCleanupThreshold = findConfigEntryByName(config, "CLEANUP_THRESHOLD");
        $scope.masterSyncCyclic = findConfigEntryByName(config, "NODE_SYNC_CYCLIC");
        $scope.masterSyncCycle = findConfigEntryByName(config, "NODE_SYNC_CYCLE");
        $scope.masterSyncOnStartup = findConfigEntryByName(config, "NODE_SYNC_ON_STARTUP");

        $scope.interfaceDoor = findConfigEntryByName(config, "NODE_DOOR_AVAILABLE");
        $scope.interfaceDoorOpeningTime = findConfigEntryByName(config, "DOOR_OPENING_TIME");

        $scope.advancedMailServer = findConfigEntryByName(config, "MAIL_SERVER");
        $scope.advancedMailPort = findConfigEntryByName(config, "MAIL_PORT");
        $scope.advancedMailUseTLS = findConfigEntryByName(config, "MAIL_USE_TLS");
        $scope.advancedMailUseSSL = findConfigEntryByName(config, "MAIL_USE_SSL");
        $scope.advancedMailUsername = findConfigEntryByName(config, "MAIL_USERNAME");
        $scope.advancedMailPassword = findConfigEntryByName(config, "MAIL_PASSWORD");

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

    $scope.startSetup = function () {
        $location.path("/master/setup" );
    };

});