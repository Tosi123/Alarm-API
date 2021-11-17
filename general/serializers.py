from rest_framework import serializers
from .models import PermitList, UserList, Message


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserList
        fields = ('alarm_type', 'alarm_group', 'target', 'extra_target','rmk')
        '''
            "user": [
                {"target": "target", "extra_target": "extra_target"}
            ]
        '''

class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('msg_gb', 'rcv_phn_id', 'callback', 'snd_msg')

class WebhookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PermitList

class BizappSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PermitList

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PermitList