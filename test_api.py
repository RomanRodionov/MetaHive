from requests import get, delete, put
#create account {user_name: 'user', password: 'user', gender: 'male'}, login and create news
print(get('http://localhost:8080/api/news').json())
print(get('http://localhost:8080/api/news/1').json())
print(get('http://localhost:8080/api/news/8').json())
print(delete('http://localhost:8080/api/news/1').json())
print(delete('http://localhost:8080/api/news/3').json())
print(put('http://localhost:8080/api/users/8', json={'user_name': 'Anna',
                 'status': 'Ha-ha', 'gender': 'female'}).json())
print(put('http://localhost:8080/api/users/1').json())
print(put('http://localhost:8080/api/users/1', json={'user_name': 'Anna',
                 'status': 'Ha-ha', 'gender': 'female'}).json())
print(get('http://localhost:8080/api/users').json())
print(get('http://localhost:8080/api/users/1').json())
print(get('http://localhost:8080/api/users/8').json())
