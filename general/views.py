# -*- coding: utf-8 -*-

import re
import json
import logging
import requests

from chardet import detect
from urllib.parse import unquote
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .models import PermitList, UserList, Message
from .serializers import UserSerializer, MessageSerializer

# Logging Start
logger = logging.getLogger(__name__)


class AlarmViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    queryset = queryset.filter(extra_target='MASTER')
    serializer_class = UserSerializer

    def encoding_check(self, data):
        try:
            result = detect(data)
            logger.debug(result)
            return result['encoding']
        except Exception as err:
            logger.error("Encoding Check Error: {}".format(err))
            return False

    def header_check(self, header):
        '''
            Header 값 검증 함수
        '''
        try:
            # IP 형식 확인
            ip_format = re.match(
                r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', header['ip-address'])
            if ip_format == None:
                return "Header IP-Address Format Error " + header['ip-address']

            # Primary-key 10자리 이상 확인
            elif len(header['primary-key']) < 10:
                return "Header Primary-Key Format Error " + header['primary-key']

            # Content-Type 확인
            if header['Content-Type'].lower() != 'application/json;charset=utf-8':
                return "Header Content-Type Format Error " + header['Content-Type']
            return True

        except KeyError as err:
            logger.error("Header Key Not Found ({})".format(str(err)))
            return "Header Key Not Found " + str(err)

        except Exception as err:
            logger.error("Header Unknown Error ({})".format(str(err)))
            return "Header Unknown Error " + str(err)

    def permit_check(self, header):
        '''
            등록된 사용자만 알람을 발송 할 수 있으며 등록 여부 확인 함수
        '''
        ip_checkset = PermitList.objects.all()
        ip_checkset = ip_checkset.filter(
            ip=header['ip-address'], primary_key=header['primary-key'])
        ip_checkset = ip_checkset.count()

        if ip_checkset == 1:
            return True
        else:
            return "IP=" + header['ip-address'] + " PK=" + header['primary-key']

    def user_select(self, utype, ugroup):
        '''
            알람 대상 그룹 조회
        '''
        user_listset = UserList.objects.all()
        user_listset = user_listset.filter(
            alarm_type=utype.upper(), alarm_group=ugroup.upper(), used_yn='Y')
        user_listset = user_listset.values('target', 'extra_target')

        if user_listset:
            return user_listset
        else:
            return False

    @action(methods=['post'], detail=False, url_path="msg/?")
    def message(self, request):
        ip = request.META['REMOTE_ADDR']
        logger.info("{} Message Send Start".format(ip))
        logger.debug("{} Message Request Header Data = {}".format(
            ip, request.headers))
        logger.debug(
            "{} Message Request Body Data = {}".format(ip, request.body))

        # Header 검증
        result = self.header_check(request.headers)
        if result == True:
            logger.info("{} Header Check Success".format(ip))
        else:
            logger.error(
                "{} Header Check Fail Status:401 ({})".format(ip, result))
            return Response(result, status=401)

        # 등록된 사용자인지 검증
        result = self.permit_check(request.headers)
        if result == True:
            logger.info("{} Registered Users".format(ip))
        else:
            logger.error(
                "{} This User Is Not Registered {}".format(ip, result))
            return Response(result, status=401)

        # 문자 발송 로직
        try:
            now = datetime.today().strftime("%Y%m%d%H%M%S")
            encoding = self.encoding_check(request.body)
            url_decode = unquote(request.body.decode(encoding))
            post_data = json.loads(url_decode)

            # Title 유무 확인
            if 'title' in post_data.keys():
                title = post_data['title']
            else:
                title = ""

            # MSG 바이트 체크 90바이트 이상시 LMS
            text_byte = len(post_data['text'].encode('euc-kr'))

            if text_byte > 90:
                msg_type = "M"
                logger.info("{} Message Size: {} Byte Sending LMS".format(
                    ip, text_byte))
            else:
                msg_type = "A"
                logger.info("{} Message Size: {} Byte Sending SMS".format(
                    ip, text_byte))

            # 개별 사용자 발송
            if post_data['group_send'].lower() == 'false':
                logger.info("{} Alarm Insert Start group=N".format(ip))
                for send in post_data['user']:
                    msg_insert = Message(
                        msg_gb=msg_type, rcv_phn_id=send['target'], callback=send['extra_target'], snd_msg=post_data['text'], subject=title, wrt_dttm=now, snd_dttm=now)
                    msg_insert.save()
                    logger.debug("{} Alarm Target = {}".format(ip, send))

            # 그룹 발송
            elif post_data['group_send'].lower() == 'true':
                logger.info("{} Alarm Insert Start group=Y".format(ip))
                for line in post_data['user']:
                    group = self.user_select('MSG', line['target'])
                    if group != False:
                        for send in group:
                            msg_insert = Message(
                                msg_gb=msg_type, rcv_phn_id=send['target'], callback=send['extra_target'], snd_msg=post_data['text'], wrt_dttm=now, snd_dttm=now)
                            msg_insert.save()
                            logger.debug(
                                "{} Alarm Target = {}".format(ip, send))

                    # 알람 대상자 조회시 없을 경우 Master 대상자에게 알람 발송
                    else:
                        logger.warn(
                            "{} Alarm Destination group not found".format(ip))
                        group = self.user_select('MSG', 'MASTER')
                        if group != False:
                            for send in group:
                                msg_insert = Message(
                                    msg_gb=msg_type, rcv_phn_id=send['target'], callback=send['extra_target'], snd_msg=post_data['text'], wrt_dttm=now, snd_dttm=now)
                                msg_insert.save()
                                logger.debug(
                                    "{} Master Alarm Target = {}".format(ip, send))
                        return Response("Alarm Destination group not found", status=301)

        # 예외 처리
        except Exception as err:
            logger.error("{} Alarm Send Fail Status:500 ({})".format(ip, err))
            return Response(str(err), status=500)

        # 알람 발송 성공 Status 200
        logger.info("{} Message Alarm Send Success".format(ip))
        return Response("Message Alarm Send Success", status=200)

    @action(methods=['post'], detail=False, url_path='webhook/?')
    def webhook(self, request):
        ip = request.META['REMOTE_ADDR']
        logger.info("{} Webhook Send Start".format(ip))
        logger.debug("{} Webhook Request Header Data = {}".format(
            ip, request.headers))
        logger.debug(
            "{} Webhook Request Body Data = {}".format(ip, request.body))

        # Header 검증
        result = self.header_check(request.headers)
        if result == True:
            logger.info("{} Header Check Success".format(ip))
        else:
            logger.error(
                "{} Header Check Fail Status:401 ({})".format(ip, result))
            return Response(result, status=401)

        # 등록된 사용자인지 검증
        result = self.permit_check(request.headers)
        if result == True:
            logger.info("{} Registered Users".format(ip))
        else:
            logger.error(
                "{} This User Is Not Registered {}".format(ip, result))
            return Response(result, status=401)

        # Webhook 발송 로직
        try:
            headers = {
                'Accept': 'application/vnd.tosslab.jandi-v2+json',
                'Content-Type': 'application/json'
            }

            form = '''{
                "body": "SYSTEM ALARM",
                "connectColor": "#8b1bfa",
                "connectInfo": [{
                    "title": "",
                    "description": ""
                }]
            }'''

            encoding = self.encoding_check(request.body)
            url_decode = unquote(request.body.decode(encoding))
            post_data = json.loads(url_decode, strict=False)

            # Title 유무 확인
            if 'title' in post_data.keys():
                title = post_data['title']
            else:
                title = ""

            # Json Data 넣기
            request_form = json.loads(form)
            request_form['connectInfo'][0]['title'] = title
            request_form['connectInfo'][0]['description'] = post_data['text']

            # 개별 사용자 발송
            if post_data['group_send'].lower() == 'false':
                logger.info("{} Webhook Request Send Start group=N".format(ip))
                for send in post_data['user']:
                    logger.debug("{} Webhook Target = {}".format(
                        ip, send['target']))
                    response = requests.post(
                        url=send['target'], headers=headers, data=json.dumps(request_form), timeout=60)
                    logger.info("{} Webhook Response Code:{}".format(
                        ip, response.status_code))
                    response.raise_for_status()

            # 그룹 발송
            elif post_data['group_send'].lower() == 'true':
                logger.info("{} Webhook Request Send Start group=Y".format(ip))
                for line in post_data['user']:
                    group = self.user_select('WEBHOOK', line['target'])
                    if group != False:
                        for send in group:
                            logger.debug("{} Webhook Target = {}".format(
                                ip, send['target']))
                            response = requests.post(
                                url=send['target'], headers=headers, data=json.dumps(request_form), timeout=60)
                            logger.info("{} Webhook Response Code:{}".format(
                                ip, response.status_code))
                            response.raise_for_status()
                    # 알람 대상자 조회시 없을 경우 Master 대상자에게 알람 발송
                    else:
                        logger.warn(
                            "{} Webhook Destination group not found".format(ip))
                        group = self.user_select('WEBHOOK', 'MASTER')
                        if group != False:
                            for send in group:
                                logger.debug(
                                    "{} Webhook Master Alarm Target = {}".format(ip, send))
                                response = requests.post(
                                    url=send['target'], headers=headers, data=json.dumps(request_form), timeout=60)
                                logger.info("{} Webhook Response Code:{}".format(
                                    ip, response.status_code))
                                response.raise_for_status()
                        return Response("Webhook Destination group not found", status=301)

        # 예외 처리
        except Exception as err:
            logger.error(
                "{} Webhook Send Fail Status:500 ({})".format(ip, err))
            return Response(str(err), status=500)

        # 알람 발송 성공 Status 200
        logger.info("{} Webhook Alarm Send Success".format(ip))
        return Response("Webhook Alarm Send Success", status=200)

    @action(methods=['post'], detail=False, url_path='mail/?')
    def mail(self, request):
        ip = request.META['REMOTE_ADDR']
        logger.info("{} Mail Send Start".format(ip))
        logger.debug("{} Mail Request Header Data = {}".format(
            ip, request.headers))
        logger.debug(
            "{} Mail Request Body Data = {}".format(ip, request.body))

        # Header 검증
        result = self.header_check(request.headers)
        if result == True:
            logger.info("{} Header Check Success".format(ip))
        else:
            logger.error(
                "{} Header Check Fail Status:401 ({})".format(ip, result))
            return Response(result, status=401)

        # 등록된 사용자인지 검증
        result = self.permit_check(request.headers)
        if result == True:
            logger.info("{} Registered Users".format(ip))
        else:
            logger.error(
                "{} This User Is Not Registered {}".format(ip, result))
            return Response(result, status=401)

        # Mail 발송 로직
        try:
            encoding = self.encoding_check(request.body)
            url_decode = unquote(request.body.decode(encoding))
            post_data = json.loads(url_decode)

            # Title 유무 확인
            if 'title' in post_data.keys():
                title = post_data['title']
            else:
                title = getattr(settings, 'EMAIL_TITLE')
            mail_text = getattr(settings, 'EMAIL_HEAD') + \
                post_data["text"] + getattr(settings, 'EMAIL_FOOT')

            # 개별 사용자 발송
            if post_data['group_send'].lower() == 'false':
                logger.info("{} Mail Request Send Start group=N".format(ip))
                for send in post_data['user']:
                    logger.debug("{} Mail Target = {}".format(
                        ip, send['target']))
                    email = EmailMessage(
                        title, mail_text, to=[send['target']])
                    email.send()
                    logger.info("{} Mail Response Code:{}".format(
                        ip, email))

            # 그룹 발송
            elif post_data['group_send'].lower() == 'true':
                logger.info("{} Mail Request Send Start group=Y".format(ip))
                for line in post_data['user']:
                    group = self.user_select('MAIL', line['target'])
                    if group != False:
                        for send in group:
                            logger.debug("{} Mail Target = {}".format(
                                ip, send['target']))
                            email = EmailMessage(
                                title, mail_text, to=[send['target']])
                            email.send()
                            logger.info("{} Mail Response Code:{}".format(
                                ip, email))
                    # 알람 대상자 조회시 없을 경우 Master 대상자에게 알람 발송
                    else:
                        logger.warn(
                            "{} Mail Destination group not found".format(ip))
                        group = self.user_select('MAIL', 'MASTER')
                        if group != False:
                            for send in group:
                                logger.debug("{} Mail Target = {}".format(
                                    ip, send['target']))
                                email = EmailMessage(
                                    title, mail_text, to=[send['target']])
                                email.send()
                                logger.info("{} Mail Response Code:{}".format(
                                    ip, email))
                        return Response("Mail Destination group not found", status=301)

        # 예외 처리
        except Exception as err:
            logger.error(
                "{} Mail Send Fail Status:500 ({})".format(ip, err))
            return Response(str(err), status=500)

        # 알람 발송 성공 Status 200
        logger.info("{} Mail Alarm Send Success".format(ip))
        return Response("Mail Alarm Send Success", status=200)

    @action(methods=['post'], detail=False, url_path='auto/?')
    def auto(self, request):
        logger.info("{} Alarm Auto Mod Send Start".format(
            request.META['REMOTE_ADDR']))

        # Webhook으로 처음 발송
        result = self.webhook(request)

        if result.status_code == 200 or result.status_code == 301 or result.status_code == 401:
            logger.debug("{}".format(result))
            return Response(status=result.status_code)
        else:
            # 1차 Fail Over MSG
            result = self.message(request)
            if result.status_code == 200 or result.status_code == 301:
                logger.debug("{}".format(result))
                return Response(status=302)
            else:
                # 2차 Fail Over Mail
                result = self.mail(request)
                if result.status_code == 200 or result.status_code == 301:
                    logger.debug("{}".format(result))
                    return Response(status=302)
                else:
                    logger.debug("{}".format(result))
                    return Response(status=304)

