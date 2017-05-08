RoseGuardenApp.service('AuthService', AuthService = function($q, localStorageService,$location, Session, User) {

    var currentUser;

    this.login = function(credentials) {
        var me = this;
        deferred = $q.defer();
        Session.create(credentials, true).then(function(user) {
            me.setLocals(credentials, user);
            return deferred.resolve(user);
        }, function(response) {
            return deferred.reject(response);
        });
        return deferred.promise
    };


    this.loadCurrentUser = function() {
        var me = this;
        console.log("Test");

        deferred = $q.defer();
        User.get(this.getCurrentUserID(),true).then(function(user) {
            currentUser = user;
            //console.log(user);
            return deferred.resolve(user);
        }, function(response) {
            console.log("Rejected");
            localStorageService.clearAll();
            $location.url("/");
            return deferred.reject(response);
        });
        return deferred.promise
    };

    this.isSupervisor = function() {
        var token = localStorageService.get('role');
        if(token) {
            if(token == 2)
                return true;
            else
                return false;
        } else {
            return false;
        }
    };


    this.isAdmin = function() {
        var token = localStorageService.get('role');
        if(token) {
            if(token == 1)
                return true;
            else
                return false;
        } else {
            return false;
        }
    };

    this.logout = function() {
        localStorageService.clearAll();
    };

    this.isAuthenticated = function() {
        var token = this.getToken();
        if (token) {
            return true
        }
        return false;
    };

    this.setLocals = function(credentials, user) {
        localStorageService.set('token' , btoa(credentials.email + ':' + credentials.password));
        localStorageService.set('userid', user.id);
        localStorageService.set('role', user.role);

    };


    this.getCurrentUserID = function () {
        return localStorageService.get('userid');
    };

    this.getToken = function() {
        return localStorageService.get('token');
    };

    return this;
});
