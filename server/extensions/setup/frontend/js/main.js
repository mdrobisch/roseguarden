//Define an angular module for our app
var RoseGuardenApp = angular.module('RoseGuardenApp', ['ngRoute','ui.bootstrap', 'ngSanitize', 'restangular']);




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
      when('/master/global', {
        templateUrl: 'partials/master/global.html',
        controller: 'MasterConfigCtrl'
      }).
      when('/master/node', {
        templateUrl: 'partials/master/node.html',
        controller: 'MasterConfigCtrl'
      }).
      when('/master/interfaces', {
        templateUrl: 'partials/master/interfaces.html',
        controller: 'MasterConfigCtrl'
      }).
      when('/master/advanced', {
        templateUrl: 'partials/master/advanced.html',
        controller: 'MasterConfigCtrl'

      }).
      otherwise({
        redirectTo: '/'
      });
});