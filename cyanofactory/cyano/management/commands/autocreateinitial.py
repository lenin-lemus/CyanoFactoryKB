from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from django.contrib.auth.models import Group

from autocreateuser import Command as create_user
from autocreategroups import Command as create_groups

class Command(BaseCommand):
    def handle(self, *args, **options):
        create_user().handle("gabriel")
        create_user().handle("admin")
        create_user().handle("guest")
        
        create_groups().handle()
        
        #everybody = Group.objects.get(name='Everybody')
        #registred = Group.objects.get(name='Registred')
        guest = Group.objects.get(name='Guest')
        admin = Group.objects.get(name='Administrator')
        #cyano_leader = Group.objects.get(name='Cyanofactory Leader')
        cyano_member = Group.objects.get(name='Cyanofactory Member')
        #non_cyano_member = Group.objects.get(name='Non-Cyanofactory Member')
        mw = Group.objects.get(name='Mittweida')
        
        print "Assigning user to groups"
        
        gabriel = User.objects.get(username="gabriel")
        gabriel.groups = [cyano_member, mw]
        gabriel.save()
        
        admin_user = User.objects.get(username="admin")
        admin_user.groups = [admin]
        admin_user.save()
        
        guest_user = User.objects.get(username="guest")
        guest_user.groups = [guest]
        guest_user.save()