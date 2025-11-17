from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def login_view(request):
    """ログイン画面"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        
        user = authenticate(request, username=user_id, password=password)
        
        if user is not None:
            auth_login(request, user)
            # セッションにユーザー情報を保存
            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.user_name
            request.session['user_type'] = user.user_type
            
            user_type_map = {
                'BASE_STAFF': '拠点倉庫担当',
                'LC_STAFF': 'LC倉庫担当',
                'ADMIN': '管理者'
            }
            request.session['user_type_display'] = user_type_map.get(user.user_type, user.user_type)
            
            return redirect('top')
        else:
            return render(request, 'login.html', {'error': 'ユーザーIDまたはパスワードが間違っています'})
    
    return render(request, 'login.html')


def logout_view(request):
    """ログアウト"""
    auth_logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def top_view(request):
    """トップ画面"""
    return render(request, 'top.html')


@login_required(login_url='/login/')
def inventory_view(request):
    """在庫照会画面"""
    return render(request, 'inventory.html')


@login_required(login_url='/login/')
def shipment_request_list_view(request):
    """出庫依頼一覧画面"""
    return render(request, 'shipment_request_list.html')


@login_required(login_url='/login/')
def shipment_request_register_view(request):
    """出庫依頼登録画面"""
    return render(request, 'shipment_request_register.html')


@login_required(login_url='/login/')
def shipment_result_list_view(request):
    """出庫実績一覧画面"""
    return render(request, 'shipment_result_list.html')
