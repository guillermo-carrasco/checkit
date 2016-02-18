angular.module('checkit')
  .controller('LoginCtrl', function($scope, $auth) {
    this.user_id = null;

    var loginCtrl = $scope;
    $scope.authenticate = function(provider) {
      $auth.authenticate(provider).then(function(response){
        loginCtrl.user_id = response.data.user_id;
        loginCtrl.listsCtrl.update_lists(response.data.user_id);
      });
    };

  });
