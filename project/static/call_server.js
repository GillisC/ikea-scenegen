/* method: for example "POST",
 * url: for example "/login"
 * body: null or FormData or String
 * on_success: function(response) or fuction(status, response) if on_error is null
 * on_error: null or function(status, response)
 * response_type: null or for example "json"
 */
function call_server(method, url, body, on_success, on_error, response_type) {
	var request = new XMLHttpRequest();
	if(response_type) {
		request.responseType = response_type;
	}

	request.onerror = function(event) {
		on_error(0, "Connection error");
	};
	request.onload = function() {
		if(on_error) {
			if(request.status != 200) {
				on_error(request.status, request.response);
			} else {
				on_success(request.response);
			}
		} else {
			on_success(request.status, request.response);
		}
	};

	request.open(method, url);
	request.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
	request.send(body);
}
