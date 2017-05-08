RoseGuardenApp.controller('MasterConfigCtrl', function($scope, $q, Config, $location) {

    var i=0;
    i++;
    $scope.isLoading = true;
    
    function loadConfig(credentials) {
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
    }

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

    loadConfig().then(function(config_unparsed) {
        config = JSON.parse(config_unparsed);
        $scope.nodeName = findConfigEntryByName(config, "NODE_NAME");
        $scope.nodePassword = findConfigEntryByName(config, "INITIAL_NODE_PASSWORD");
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
        $scope.interfaceDoorKeymask = findConfigEntryByName(config, "DOOR_KEYMASK");
        $scope.interfaceDoorKeymaskForm = [];
        validKeyMask = parseInt($scope.interfaceDoorKeymask.value);
        for(var i = 0;i < 8; i++) {
            if ( ((0x01 << i) & validKeyMask) != 0)
                $scope.interfaceDoorKeymaskForm.push(true);
            else
                $scope.interfaceDoorKeymaskForm.push(false);
        }

        $scope.advancedMailServer = findConfigEntryByName(config, "MAIL_SERVER");
        $scope.advancedMailPort = findConfigEntryByName(config, "MAIL_PORT");
        $scope.advancedMailUseTLS = findConfigEntryByName(config, "MAIL_USE_TLS");
        $scope.advancedMailUseSSL = findConfigEntryByName(config, "MAIL_USE_SSL");
        $scope.advancedMailUsername = findConfigEntryByName(config, "MAIL_USERNAME");
        $scope.advancedMailPassword = findConfigEntryByName(config, "MAIL_PASSWORD");

        $scope.isLoading = false;


    }, function(response) {
        console.log("loaded");

    });


    $scope.randmoizeGlobalKey = function() {
        var token = "";
        for(var j= 0;j < 6;j++) {
            for (var i = 0; i < 2; i++) {
                token += Math.floor(Math.random()*16).toString(16);
            }
            if (j != 5)
                token += "-";
        }
        $scope.masterGlobalRfidKey.value = token;
    };


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
            $location.path("/master/setup" );
        }, function(response) {
            console.log("rejected");

        });
    };

});