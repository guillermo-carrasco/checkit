// Angular js application
(function() {
  var app = angular.module('checkit', ['satellizer'])
    .config(function($authProvider){
      $authProvider.github({
        clientId: ''
      });
    });
})();
