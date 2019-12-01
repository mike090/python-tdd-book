from urllib import request

def make_sure_http_server_runing():
	assert request.urlopen('http://localhost:8000').getcode() == 200


if __name__ == '__main__':
	make_sure_http_server_runing()