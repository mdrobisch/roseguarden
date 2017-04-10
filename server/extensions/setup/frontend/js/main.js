//Define an angular module for our app
var RoseGuardenApp = angular.module('RoseGuardenApp', ['ngRoute','ui.bootstrap', 'ngSanitize', 'restangular','ngScrollbar']);




RoseGuardenApp.config(function($routeProvider, RestangularProvider) {

    //RestangularProvider.setBaseUrl('http://localhost:5000');

    console.log(window.location.hostname);
    //RestangularProvider.setBaseUrl('http://' + window.location.hostname + ':5000');
    RestangularProvider.setBaseUrl('http://' + window.location.hostname + '/api/v1/');
    //RestangularProvider.setBaseUrl('http://localhost:5000');

    $routeProvider.
      when('/', {
        templateUrl: 'partials/welcome.html'
      }).
      when('/start', {
        templateUrl: 'partials/start.html'
      }).
      when('/master/config', {
      templateUrl: 'partials/master/config.html',
      controller: 'MasterConfigCtrl'
      }).
      when('/master/setup', {
      templateUrl: 'partials/master/setup.html',
      controller: 'MasterSetupCtrl'
      }).
      when('/slave/config', {
      templateUrl: 'partials/slave/config.html',
      controller: 'SlaveConfigCtrl'
      }).
      otherwise({
        redirectTo: '/'
      });
});