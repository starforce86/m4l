import os
import string, random
#os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

#import conf.settings
import django
django.setup()

from django.contrib.auth.models import User

passwd_chars = [string.ascii_letters[:26],
                string.digits,
                string.ascii_letters[26:],
                string.punctuation]
used_passwords = []
 
def get_random_password(length=20):
    pwd = []
    chars = random.choice(passwd_chars)
    while len(pwd) < length:
        pwd.append(random.choice(chars))
        chars = random.choice(list(set(passwd_chars) - set([chars])))
    return "".join(pwd)
    
users = User.objects.filter(is_superuser=True)
for u in users:
    print(u)
    new_pwd = get_random_password(20)
    while new_pwd in used_passwords:
        new_pwd = get_random_password(20)
    used_passwords.append(new_pwd)
    #print(new_pwd)
    u.set_password(new_pwd)
    u.save()
