#!/usr/bin/env bash

# Auto Send mode is only available for group shipping.
# Use :
# ./send_auto.sh [msg] [group_name] [title]
#
# Example
# ./send_auto.sh "TESTSMS" ADMIN "TEST TITLE"

LANG="ko_KR.UTF-8"
SEND_URL="http://monitor.standard.kr:8282/alarm/send/auto/"
ip=`/sbin/ifconfig | grep '\<inet\>' | sed -n '1p' | tr -s ' ' | cut -d ' ' -f3 | cut -d ':' -f2`
host=`hostname`
pk=`/sbin/ifconfig |grep -iE "ether|HWaddr" |tr -s ' ' |awk -F"ether|HWaddr" '{print $2}' |cut -d ' ' -f2 |head -1`
ARG1=$1
ARG2=$2
ARG3=$3

if [[ "x${ARG1}" == "x" ]] || [[ "x${ARG2}" == "x" ]];
then
    echo '
    Please enter required items.
    # Auto Send mode is only available for group shipping.
    # Use :
    # ./send_auto.sh [msg] [group_name] [title]
    #
    # Example
    # ./send_auto.sh "TESTSMS" ADMIN "TEST TITLE"
    '
    exit 9
fi

function group_mod(){
    cat <<EOF
    {
        "text": "${ARG1}",
        "title": "${ARG3}",
        "group_send": "True",
        "user": [{"target": "${ARG2}"}]
    }
EOF
}

STATUS=$(curl ${SEND_URL} \
-m300 -s -o /dev/null -w %{http_code} \
-H "ip-address: ${ip}" \
-H "primary-key: ${pk}" \
-H "hostname: ${host}" \
-H "Content-Type: application/json;charset=utf-8" \
--data-binary "$(group_mod)")

echo ${STATUS}

