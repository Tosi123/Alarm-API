#!/usr/bin/env bash

PWD=`pwd`
LANG=ko_KR.utf8
PROCESS_NAME=`basename ${PWD}`
PORT="8282"
PYTHON_PATH="/usr/bin/python"
OPTION=""

start() {
    cnt=`ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |wc -l`
    if [[ ${cnt} -eq 0 ]]; then
        nohup ${PYTHON_PATH} ${OPTION} -X${PROCESS_NAME} ./manage.py runserver 0.0.0.0:${PORT} >> ./logs/${PROCESS_NAME}.out 2>> ./logs/${PROCESS_NAME}.err &
        sleep 3
        cnt=`ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |wc -l`
        if [[ ${cnt} -gt 0 ]]; then
            echo "Process START Success!! CNT:${cnt}"
        else
            echo "Process START Fail!! CNT:${cnt}"
        fi
    else
        echo "Process Already Running"
    fi
}

stop() {
    cnt=`ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |wc -l`
    if [[ ${cnt} -gt 0 ]]; then
        for (( i=0; i <= 10; i++ )); do
            kill `ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |awk '{print $2}'`
            echo "."
            sleep 1s

            pid_chk=`ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |wc -l`
            if [[ ${pid_chk} -eq 0 ]]; then
                echo -e "Process STOP Success!!"
                exit
            fi

            if [[ ${i} -eq 9 ]];then
                kill -9 `ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |awk '{print $2}'`
                sleep 2s
                pid_chk=`ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |wc -l`
                if [[ ${pid_chk} -eq 0 ]]; then
                    echo -e "Process Force STOP Success!!"
                    exit
                else
                    echo -e "Process Force STOP Fail!!"
                    ps -ef |grep "${PROCESS_NAME}.py" |grep -v grep
                    exit
                fi
            fi
        done
    else
        echo "Process Already Terminated"
    fi
}

status() {
    cnt=`ps -ef |grep "X${PROCESS_NAME}" |grep ${PORT} |grep manage.py |grep -v grep |wc -l`
    if [[ ${cnt} -gt 0 ]]; then
        echo "Process Started!! CNT:${cnt}"
    else
        echo "Process Does Not Start!!"
    fi
}

if [[ -z ${1} ]]; then
    echo "USE ./Shell START|STOP|STATUS"
    exit
fi

case "$1" in
  "START"|"start")
    start
    ;;
  "STOP"|"stop")
    stop
    ;;
  "STATUS"|"status")
    status
    ;;
  *)
    echo "This Option Is Not Supported."
    ;;
esac
