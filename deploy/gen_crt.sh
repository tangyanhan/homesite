#!/bin/sh

help()
{
    echo "Example: ./gen_crt.sh root aes128 2048 365 \"/CN=CustomCA\""
    echo "Example: ./gen_crt.sh sign aes128 2048 365 \"/CN=www.mysite.com\" ca.key ca.cer"
    echo "key_length: 1024|2048|4096"
    methods="aes128|aes192|aes256|camellia128|camellia192|camellia256|des|des3|idea"
    echo "Supported encryption methods:" $methods
    exit 1
}

operation=$1
method=$2
key_length=$3
expire_days=$4
subj=$5
ca_key=$6
ca_cer=$7

RED="\033[0;31m"
GREEN="\033[0;32m"
NC="\033[0m"


if [ "$operation" = "root" ];then
    if [ $# -ne 5 ];then
        echo "${RED}Invalid argument num:$#${NC}"
        help
    fi
elif [ "$operation" = "sign" ];then
    if [ $# -ne 7 ];then
        echo "${RED}Invalid argument num:$#${NC}"
        help
    fi
else
    echo "${RED}Invalid operation $operation${NC}"
    help
fi

echo "Operation" $operation

case $method in
    aes128|aes192|aes256|camellia128|camellia192|camellia256|des|des3|idea)
        echo "Using cryption method:" $method
        ;;
    *)
        echo "Wrong parameters"
        help
        ;;
esac

case $key_length in
    1024|2048|4096)
        echo "RSA Key length:" $key_length
        ;;
    *)
        echo "Wrong RSA key length"
        help
        ;;
esac

if [$expire_days -lt 0]; then
    echo "Invalid expire days:" $expire_days
    help
fi

if [ "$operation" = "root" ];then
    echo "Creating Root CA..."
    openssl genrsa -$method -out ca.key $key_length
    openssl req -x509 -new -key ca.key -out ca.cer -days 750 -subj $subj
    echo "${GREEN}Please distribute ca.cer anywhere needed"
    echo "${RED}Please keep ca.key in a private place${NC}"
elif [ "$operation" = "sign" ];then
    openssl genrsa -$method -out cert.key $key_length
    openssl req -new -out cert.req -key cert.key -subj $subj
    openssl x509 -req -in cert.req -out cert.cer -CAkey $ca_key -CA $ca_cer -days $expire_days -CAcreateserial
    -CAserial serial
    echo "${GREEN}Please distribute cert.cer freely"
    echo "${RED}Please keep cert.key privately${NC}"
else
    echo "Unknown operation: $operation"
    help
fi

