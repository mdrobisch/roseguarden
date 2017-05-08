//Define an angular module for our app
var RoseGuardenApp = angular.module('RoseGuardenApp', ['ngRoute','ui.bootstrap', 'ngSanitize', 'chart.js', 'angularNumberPicker','restangular', 'LocalStorageModule', 'smart-table']);


RoseGuardenApp.run(function($location, Restangular, AuthService) {

    Restangular.setFullRequestInterceptor(function(element, operation, route, url, headers, params, httpConfig) {
        if (AuthService.isAuthenticated()) {
            headers['Authorization'] = 'Basic ' + AuthService.getToken();
        }
        return {
            headers: headers
        };
    });

    Restangular.setErrorInterceptor(function(response, deferred, responseHandler) {
        if (response.config.bypassErrorInterceptor) {
            return true;
        } else {
            switch (response.status) {
                case 401:
                    //AuthService.logout();
                    //$location.path('/sessions/create');
                    break;
                default:
                    throw new Error('No handler for status code ' + response.status);
            }
            return false;
        }
    });
});

//Define Routing for app
//Uri /AddNewOrder -> template add_order.html and Controller AddOrderController
//Uri /ShowOrders -> template show_orders.html and Controller AddOrderController
RoseGuardenApp.config(function($routeProvider, RestangularProvider) {

    //RestangularProvider.setBaseUrl('http://localhost:5000');

    console.log(window.location.hostname);
    //RestangularProvider.setBaseUrl('http://' + window.location.hostname + ':5000');
    RestangularProvider.setBaseUrl('http://' + window.location.hostname + '/api/v1/');
    //RestangularProvider.setBaseUrl('http://localhost:5000');


    var redirectIfAuthenticated = function(route) {
        return function($location, $q, AuthService) {

            var deferred = $q.defer();

            if (AuthService.isAuthenticated()) {
                deferred.reject();
                $location.path(route);
            } else {
                deferred.resolve()
            }

            return deferred.promise;
        }
    };

    var redirectIfNotAuthenticated = function(route) {
        return function($location, $q, AuthService) {

            console.log("redirectIfNotAuthenticated");

            var deferred = $q.defer();

            if (! AuthService.isAuthenticated()) {
                deferred.reject();
                $location.path(route);
            } else {
                deferred.resolve()
            }

            return deferred.promise;
        }
    };

    $routeProvider.
      when('/', {
        templateUrl: 'partials/main/home.html',
        controller: 'HomeCtrl',
        resolve: {
            redirectIfNotAuthenticated: redirectIfNotAuthenticated('/login')
        }

      }).
      when('/admin', {
        templateUrl: 'partials/main/admin.html',
        controller: 'AdminSpaceCtrl'
      }).
      when('/supervisor', {
        templateUrl: 'partials/main/supervisor.html',
        controller: 'SupervisorTabCtrl'
      }).
      when('/login', {
        templateUrl: 'partials/session/login.html',
        controller: 'LoginCtrl'
      }).
      when('/register', {
        templateUrl: 'partials/session/register.html',
        controller: 'RegisterCtrl'
      }).
      when('/logout', {
        templateUrl: 'partials/session/logout.html',
        controller: 'LogoutCtrl'
      }).
      when('/lostpassword', {
        templateUrl: 'partials/session/lostpassword.html',
        controller: 'LostPasswordCtrl'
      }).
      otherwise({
        redirectTo: '/'
      });
});