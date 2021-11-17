from django.db import models


class PermitList(models.Model):
    ip = models.CharField(max_length=15)
    primary_key = models.CharField(max_length=20, unique=True)
    hostname = models.CharField(max_length=255)
    rmk = models.CharField(max_length=300, null=True)
    create_dttm = models.DateTimeField(auto_now_add=True)
    update_dttm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alarm_permit_list"
        indexes = [
            models.Index(fields=['primary_key']),
        ]

class UserList(models.Model):
    alarm_type = models.CharField(max_length=10)
    alarm_group = models.CharField(max_length=10)
    target = models.CharField(max_length=100)
    extra_target = models.CharField(max_length=100, null=True)
    used_yn = models.CharField(max_length=1, default="Y")
    rmk = models.CharField(max_length=300, null=True)
    create_dttm = models.DateTimeField(auto_now_add=True)
    update_dttm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alarm_user_list"
        indexes = [
            models.Index(fields=['alarm_type', 'alarm_group']),
        ]

class Message(models.Model):
    # cmp_msg_id = models.CharField(max_length=20, primary_key=True)
    cmp_msg_id = models.AutoField(primary_key=True)
    msg_group_id = models.CharField(max_length=20, default="0")
    cmp_usr_id = models.CharField(max_length=5, default="00000")
    odr_fg = models.CharField(max_length=1, default="2")
    msg_gb = models.CharField(max_length=1, default="A")
    wrt_dttm = models.CharField(max_length=14, null=True, blank=True)
    snd_dttm = models.CharField(max_length=14)
    sms_gb = models.CharField(max_length=1, default="1")
    used_cd = models.CharField(max_length=3, default="00")
    rcv_phn_id = models.CharField(max_length=15)
    callback = models.CharField(max_length=15)
    snd_msg = models.CharField(max_length=4000)
    subject = models.CharField(max_length=60, null=True, blank=True)
    snd_phn_id = models.CharField(max_length=15, null=True, blank=True)
    reg_snd_dttm = models.CharField(max_length=14, null=True, blank=True)
    reg_rcv_dttm = models.CharField(max_length=14, null=True, blank=True)
    expire_val = models.IntegerField(default="0", null=True, blank=True)
    sms_st = models.CharField(max_length=1, default="0")
    rslt_val = models.IntegerField(default="99", null=True, blank=True)
    cmp_snd_dttm = models.CharField(max_length=14, null=True, blank=True)
    cmp_rcv_dttm = models.CharField(max_length=14, null=True, blank=True)
    rcv_mno_cd = models.CharField(max_length=5, null=True, blank=True)
    rsrvd_id = models.CharField(max_length=20, null=True, blank=True)
    rsrvd_wd = models.CharField(max_length=32, null=True, blank=True)
    assign_cd = models.CharField(max_length=1, null=True, blank=True)
    snd_gb = models.CharField(max_length=1, default="N", null=True, blank=True)
    snd_skt_fg = models.CharField(max_length=1, default="N", null=True, blank=True)
    snd_ktf_fg = models.CharField(max_length=1, default="N", null=True, blank=True)
    snd_lgt_fg = models.CharField(max_length=1, default="N", null=True, blank=True)
    nat_cd = models.CharField(max_length=3, default="82", null=True, blank=True)
    content_group_id = models.CharField(max_length=20, default="0")
    msg_id = models.CharField(max_length=20, null=True, blank=True)
    auth_seq = models.CharField(max_length=5, null=True, blank=True)
    agt_node_id = models.CharField(max_length=20, null=True, blank=True)
    read_reply_val = models.IntegerField(null=True, blank=True)
    read_reply_dttm = models.CharField(max_length=14, null=True, blank=True)
    class Meta:
        db_table = "std_msg_send"
        indexes = [
            models.Index(fields=['snd_dttm', 'sms_st', 'rslt_val']),
        ]

