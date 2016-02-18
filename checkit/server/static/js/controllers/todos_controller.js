angular.module('checkit')
.controller('TodoListController', ['$http', function($http) {

  this.new_todo_list = {}
  this.new_item = {}
  this.lists = [];

  // Updates lists attribute of the controller
  var ctrl = this;
  this.update_lists = function(user_id) {
    $http.get('/v1/users/' + user_id + '/lists').success(function(data){
      ctrl.lists = data['lists'];
    });
  };

  this.addTodoList = function(user_id) {
    var list_data = {"description": this.new_todo_list.description};
    $http.post('/v1/users/' + user_id + '/lists', list_data).success(function(data){
      ctrl.lists.push(data);
    });
    this.new_todo_list = {};
  }

  this.addTodoItem = function(user_id, list_data){
    var list_id = list_data['id'];
    var item_data = {"description": ctrl.new_item[list_id], "todo_list_id": list_id};
    $http.post('/v1/users/' + user_id + '/lists/' + list_id + '/items', item_data).success(function(data){
      list_data['items'].push(data);
      ctrl.new_item[list_id] = '';
    });
  };

}]);
