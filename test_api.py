from requests import get, post, delete, put
#create account {user_name: 'user', password: 'user', gender: 'male'}, login and create news
print(get('http://localhost:8080/news').json())
print(get('http://localhost:8080/').json())
print(get('http://localhost:8080/news/1').json())
print(get('http://localhost:8080/news/8').json())
print(delete('http://localhost:8080/news/1').json())
print(delete('http://localhost:8080/news/3').json())
print(put('http://localhost:8080/users/8', json={'user_name': 'Anna',
                 'status': 'Ha-ha', 'gender': 'female'}).json())
print(put('http://localhost:8080/users/1').json())
print(put('http://localhost:8080/users/1', json={'user_name': 'Anna',
                 'status': 'Ha-ha', 'gender': 'female'}).json())
print(get('http://localhost:8080/users').json())
print(get('http://localhost:8080/users/1').json())
print(get('http://localhost:8080/users/8').json())
