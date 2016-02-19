// Angular js application
(function() {
  var app = angular.module('checkit', ['satellizer'])
    .config(function($authProvider){
      $authProvider.github({
        clientId: 'c0d6b84e7bd977d139a0'
      });
    });
})();
