#!/bin/sh

help()
{
    echo "Example: ./gen_crt.sh aes128 2048 365 myssl.crt"
    echo "Parameters: encrypt_method key_length expire_days"    
    echo "key_length: 1024|2048|4096"
    methods="aes128|aes192|aes256|camellia128|camellia192|camellia256|des|des3|idea"
    echo "Supported encryption methods:" $methods
    exit 1
}

gen_crt()
{
    method=$1
    key_length=$2
    expire_days=$3
    crt_name=$4
    
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

    dir_name='gen_crt_tmp'
    if [-e $dir_name]; then
        echo "Directory already exists:" $dir_name " Deleting..."
        rm -rf dir_name
        echo "Deleted"
    fi

    mkdir $dir_name
    cd $dir_name
    openssl genrsa -$method -passout pass:x -out ssl.pass.key $key_length
    openssl rsa -passin pass:x -in ssl.pass.key -out ssl.key
    openssl req -new -key ssl.key -out ssl.csr
    openssl x509 -req -days $expire_days -in ssl.csr -signkey ssl.key -out ssl.crt
    cp ssl.crt ../$crt_name
    cd ..
    rm -rf $dir_name
}

if [$# -ne 4]; then
    echo "Argument error!"
    help
fi

gen_crt $1 $2 $3 $4
