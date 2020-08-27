var pixellot = axios.create({
	  baseURL: 'http://52.82.60.3:5000/',
	  headers: {'Authorization': 'pixellot ' + localStorage.getItem('token')}		
});
var pixellot_login = axios.create({
	  baseURL: 'http://52.82.60.3:5000/'
});

