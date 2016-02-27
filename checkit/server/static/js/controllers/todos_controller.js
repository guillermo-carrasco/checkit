angular.module('checkit')
.controller('TodoListController', ['$http', function($http) {

  // Two-way bingin objects for the front end. When these are updated, so it is the front page.
  this.new_todo_list = {};
  this.new_item = {};
  this.lists = [];
  this.user = {};

  // copy the scope to an external variable to be used within $http calls
  var ctrl = this;

  // Get user information and update lists
  this.get_user = function() {
    $http.get('/user').success(function(user){
      ctrl.user = user;
      $http.get('/v1/users/' + ctrl.user['id'] + '/lists').success(function(data){
        ctrl.lists = data['lists'];
      });
    });
  };
  this.get_user();


  this.addTodoList = function() {
    var list_data = {"description": this.new_todo_list.description};
    $http.post('/v1/users/' + ctrl.user['id'] + '/lists', list_data).success(function(data){
      // Update local array of lists after creating the new list
      data['items'] = [];
      ctrl.lists.push(data);
    });
    this.new_todo_list = {};
  };

  this.delete_list = function(list) {
    var user_id = list.user_id;
    $http.delete('/v1/users/' + user_id + '/lists/' + list.id).success(function(data){
      // Remove list from the array of lists
      ctrl.lists.splice(ctrl.lists.indexOf(list), 1);
    });
  };

  this.addTodoItem = function(list_data){
    var list_id = list_data['id'];
    var user_id = ctrl.user['id'];
    var item_data = {"description": ctrl.new_item[list_id], "todo_list_id": list_id};
    $http.post('/v1/users/' + user_id + '/lists/' + list_id + '/items', item_data).success(function(data){
      list_data['items'].push(data);
      ctrl.new_item[list_id] = '';
    });
  };

  this.updateItem = function(list, item) {
    // Get item's list index, and change the attribute in the item
    var l_index = ctrl.lists.indexOf(list);
    var i_index = ctrl.lists[l_index]['items'].indexOf(item);
    var user_id = ctrl.user['id'];
    ctrl.lists[l_index]['items'][i_index].checked = !ctrl.lists[l_index]['items'][i_index].checked;

    $http.put('/v1/users/' + user_id + '/lists/' + item['todo_list_id'] + '/items/' + item['id'], item).success(function(data){
      console.log("Item updated correctly");
    });
  };

}]);
