#!/bin/bash
SIP_FLAG="From: <sip:"
FLAG_LEN=${#SIP_FLAG}
MY_NUM="2422435"
echo -e "Me" > "Caller$MY_NUM"


read_dom () {
    local IFS=\>
    read -d \< ENTITY CONTENT
}

export -f read_dom

queryapi() {
    echo "CAUGHT $1"
    NOZERO=`echo $1 | cut -c 3-`
    LAST_CALL_NUM=`cat LastCallNumber`
    if [[ $LAST_CALLER != $1 ]]
    then
        if [[ ${NOZERO##*[!0-9]*} ]]
        print "IS A NUMBER = $1"
        then
            echo "$1" > LastCallNumber
            curl -s "http://webtrans.reallysimplesystems.com/api/api.v2.asmx/GetContacts?CustomerId=1107&APIPassword=elasticcloud.47&SearchField=Custom07&SearchValue=$NOZERO" > last_query_mobile.xml &&
            curl -s "http://webtrans.reallysimplesystems.com/api/api.v2.asmx/GetContacts?CustomerId=1107&APIPassword=elasticcloud.47&SearchField=Custom05&SearchValue=$NOZERO" > last_query_phone.xml
            # while read_dom; do
            #     echo -e "$ENTITY : $CONTENT" | grep -E '^[A-Z]'
            # done < last_query_mobile.xml >> LastCaller
            # cat LastCaller
        fi
    fi
    return 0
}

export -f queryapi

sudo tcpdump -W 1 -w sniff_logs.txt -i eth0 udp | grep "$SIP_FLAG" | cut -c `expr $FLAG_LEN + 1`- |  cut -d "@" -f 1 | tee /dev/tty | xargs -I THIS bash -c "queryapi THIS"

#real
# sudo tcpdump -A udp | grep "$1" | cut -c $FLAG_LEN- |  cut -d "@" -f 1 | xargs -I number queryApi number

# "From: <sip:2422435@sip.gradwell.com>;tag=4dd2b9e0-1747-4e8a-92d7-74e98eec70ca"

# echo "From: <sip:00353833822713@sip.gradwell.com>" 
#   00353833822713
#   07714204512