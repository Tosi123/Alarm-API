#!/usr/bin/env bash

# Use :
# ./send_mail.sh [msg] [group "N"] [email] [title]
# ./send_mail.sh [msg] [group "Y"] [group_name] [title]
#
# Example
# 1. ./send_mail.sh "TESTSMS" N support@standard.kr "TEST TITLE"
# 2. ./send_mail.sh "TESTSMS" Y ADMIN "TEST TITLE"

LANG="ko_KR.UTF-8"
SEND_URL="http://monitor.standard.kr:8282/alarm/send/mail/"
ip=`/sbin/ifconfig | grep '\<inet\>' | sed -n '1p' | tr -s ' ' | cut -d ' ' -f3 | cut -d ':' -f2`
host=`hostname`
pk=`/sbin/ifconfig |grep -iE "ether|HWaddr" |tr -s ' ' |awk -F"ether|HWaddr" '{print $2}' |cut -d ' ' -f2 |head -1`
ARG1=$1
ARG2=$2
ARG3=$3
ARG4=$4

if [[ "x${ARG1}" == "x" ]] || [[ "x${ARG2}" == "x" ]] || [[ "x${ARG3}" == "x" ]]
then
    echo '
    Please enter required items.
    # Use :
    # ./send_mail.sh [msg] [group "N"] [email] [title]
    # ./send_mail.sh [msg] [group "Y"] [group_name] [title]
    #
    # Example
    # 1. ./send_mail.sh "TESTSMS" N support@standard.kr "TEST TITLE"
    # 2. ./send_mail.sh "TESTSMS" Y ADMIN "TEST TITLE"
    '
    exit 9
fi

function group_mod(){
    cat <<EOF
    {
        "text": "${ARG1}",
        "title": "${ARG4}",
        "group_send": "True",
        "user": [{"target": "${ARG3}"}]
    }
EOF
}

function target_mod(){
    cat <<EOF
    {
        "text": "${ARG1}",
        "title": "${ARG4}",
        "group_send": "False",
        "user": [{"target": "${ARG3}"}]
    }
EOF
}

if [[ "${ARG2}" == "N" ]]; then
    STATUS=$(curl ${SEND_URL} \
    -m300 -s -o /dev/null -w %{http_code} \
    -H "ip-address: ${ip}" \
    -H "primary-key: ${pk}" \
    -H "hostname: ${host}" \
    -H "Content-Type: application/json;charset=utf-8" \
    --data-binary "$(target_mod)")
else
    STATUS=$(curl ${SEND_URL} \
    -m300 -s -o /dev/null -w %{http_code} \
    -H "ip-address: ${ip}" \
    -H "primary-key: ${pk}" \
    -H "hostname: ${host}" \
    -H "Content-Type: application/json;charset=utf-8" \
    --data-binary "$(group_mod)")
fi

echo ${STATUS}

