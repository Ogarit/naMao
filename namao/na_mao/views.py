from django.shortcuts import render, redirect
import requests
import json

message_register = None
auth = None
token = None


def home(request):
    global auth

    response_api_categories = requests.get('https://namao.online/api/categories')

    if response_api_categories.status_code == 200:
        response_categories = response_api_categories.json()
        data_categories = response_categories.get('data')
        destaque = False

        if request.method == 'POST' and request.POST.get('search') != '':
            search = request.POST.get('search')
            response_api_services = requests.get(f'https://namao.online/api/services/search/{search}')
        else:
            response_api_services = requests.get('https://namao.online/api/emphasis/services')
            destaque = True

        if response_api_services.status_code == 200:
            response_services = response_api_services.json()

            try:
                data_services = response_services.get('data')
            except AttributeError:
                data_services = response_services

            categories = list()

            for i in data_categories:
                for j in data_services:
                    if i.get('id') == j.get('category_id'):
                        categories.append(i)

                        break

            return render(request, 'home.html', {'categories': categories, 'services': data_services,
                                                 'destaque': destaque, 'auth': auth})
        elif response_api_services.status_code == 404:
            response_services = response_api_services.json()
            message = response_services.get('message')

            return render(request, 'home.html', {'message': message})
        else:
            return render(request, 'home.html')


def login(request):
    global auth
    global token
    global message_register

    if request.method == 'POST':
        data = {
            "email": request.POST.get('email'),
            "password": request.POST.get('password')
        }

        data_json = json.dumps(data)

        response_api = requests.post('https://namao.online/api/sessions', data=data_json,
                                     headers={'Content-Type': 'application/json'})

        if response_api.status_code == 200:
            response = response_api.json()
            auth = response.get('user')
            token = response.get('authorization')

            return redirect('/')
        elif response_api.status_code == 401:
            return render(request, 'login.html', {'message': 'Invalido! E-mail ou senha incorretas!'})

    return render(request, 'login.html', {'message_register': message_register})


def register(request):
    if request.method == 'POST':
        global message_register

        if request.POST.get('password') == request.POST.get('password_'):
            data = {
                "name": request.POST.get('name'),
                "email": request.POST.get('email'),
                "cep": request.POST.get('cep'),
                "phone": request.POST.get('phone'),
                "password": request.POST.get('password')
            }

            data_json = json.dumps(data)

            response_api = requests.post('https://namao.online/api/users', data=data_json,
                                         headers={'Content-Type': 'application/json'})

            if response_api.status_code == 201:
                response = response_api.json()
                message_register = response.get('message')

                return redirect('/login')
            elif response_api.status_code == 200:
                if request.POST.get('name') and request.POST.get('email') and request.POST.get('cep') and\
                        request.POST.get('phone'):
                    return render(request, 'register.html', {'message': 'Usuário já existente!'})
                else:
                    return render(request, 'register.html')
        else:
            return render(request, 'register.html', {'message': 'As senhas são diferentes!'})

    return render(request, 'register.html')


def register_services(request):
    global auth
    global token

    message = None

    if request.method == 'POST':
        data = {
            "name": request.POST.get('name'),
            "description": request.POST.get('description'),
            "observation": "Nenhuma observação no momento.",
            "price": request.POST.get('price'),
            "discount": request.POST.get('discount'),
            "category_id": request.POST.get('category_id'),
            "user_id": auth.get('id'),
            "order": 1
        }

        data_json = json.dumps(data)

        response_api_create = requests.post('https://namao.online/api/services', data=data_json,
                                            headers={'Content-Type': 'application/json',
                                                     'Authorization': f'Bearer {token.get("token")}'})

        if response_api_create.status_code == 201:
            response_create = response_api_create.json()
            message = response_create.get('message')

    response_api = requests.get('https://namao.online/api/categories')

    if response_api.status_code == 200:
        response = response_api.json()
        categories = response.get('data')

        if message:
            return render(request, 'registerServices.html', {'auth': auth, 'categories': categories,
                                                             'message': message})
        else:
            return render(request, 'registerServices.html', {'auth': auth, 'categories': categories})
    else:
        return render(request, 'registerServices.html', {'auth': auth})


def services(request, service_id):
    global auth

    response_api = requests.get(f'https://namao.online/api/services/{service_id}')

    if response_api.status_code == 200:
        response = response_api.json()
        service = response.get('data')[0]

        return render(request, 'services.html', {'auth': auth, 'service': service})
    else:
        return render(request, 'services.html', {'auth': auth})


def logout(request):
    global auth
    global token

    auth = None
    token = None

    return redirect('/')
