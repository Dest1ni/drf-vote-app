from .models import User


def user_exists(id):
    try:
        user = User.objects.get(id = id)
        data = {'user':user,'exists':True}
        return data
    except:
        return {'exists': False}