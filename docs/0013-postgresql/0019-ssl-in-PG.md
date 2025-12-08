---
title: SSL in PG
date: 2024-02-12T20:30:38+08:00
draft: false
---


## Overview

In application level, ”PostgreSQL“ has native supports for using SSL connections. This requires that OpenSSL is installed on both client and server systems and that support in PostgreSQL is enabled at build time.

With SSL, we can:

1. Encrypted data on Internet transmission
2. Allow client to authorize the server(PostgreSQL), which can protect the client from connecting to the attacker’s server
3. Allow server to authorize the client, which can stop the attacker from connecting to the database even if password leak.

## Just encrypt internet transmission

### build binary from source

just configure with `-with-openssl`  option.  You may need to install `ssl-dev` tools first

```bash
sudo apt-get install libssl-dev
```

Below is a building example:

```bash
export build_dir=/home/dev/build
export data_dir=/home/dev/data
export superuser=postgres
export defaultdb=test

${build_dir}/bin/pg_ctl -D ${data_dir} stop
rm -rf build
rm -rf data

cd postgresql
git clean -xdf
./configure \
    --prefix=${build_dir} \
    --enable-debug \
    --enable-cassert \
    --with-tcl \
    --with-perl \
    --with-python \
    --enable-debug \
    --without-icu \
    --with-openssl \
    CC=/usr/bin/gcc \
    CFLAGS='-O0 -pipe -Wall -g3'

# export CLFAGS="-O0 -Wall -g3"
# export CPPLFAGS="-O0 -Wall -g3"

make -j8 && make install
make -C contrib install
${build_dir}/bin/initdb --username=${superuser} --pgdata=${data_dir}
${build_dir}/bin/pg_ctl -D ${data_dir} -l ${data_dir}/logfile start
${build_dir}/bin/psql -U${superuser} postgres -c "create database ${defaultdb};"
echo "----------------- all finished -----------------------"
echo "use ************** "
echo "[ ${build_dir}/bin/psql -U${superuser} ${defaultdb} ] "
echo "to connect postgresql"
cd ..
```

### Configure ssl on server

#### prepare a certification

use `openssl` command to generate one. The `127.0.0.1` means that the certification only protects localhost connections

```bash
# generate root certification
openssl req -new -x509 -days 3650 -nodes \
  -out ca.crt -keyout ca.key -subj "/CN=root-server-ca"

# generate csr and key
openssl req -new -nodes -text -out server.csr \
  -keyout server.key -subj "/CN=127.0.0.1"

# generate certification
openssl x509 -req -in server.csr -text -days 365 \
  -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt
```

#### configure in `$PGDATA`

copy the `key` and `crt` to `$PGDATA`

```bash
export $PGDATA=/home/dev/data
cp server.key $PGDATA/.
cp server.crt $PGDATA/.
```

configure in `postgresql.conf`  

```bash
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

And (re)start the server

#### connect and test

```bash
psql "host=127.0.0.1 port=5432 dbname=postgres user=postgres sslmode=require"
```

![Untitled](https://raw.githubusercontent.com/mobilephone724/blog_pictures/master/tls-connection.2024_02_12_1707741369.png)

## Server sides Authorization

Note that the client hasn’t check the certification of the server now. Check in this way:

```bash
PGSSLROOTCERT=ca.crt \
psql "host=127.0.0.1 port=5432 dbname=postgres user=postgres sslmode=require"
```

## Client sides Authorization

Generate certification similarly

```bash
openssl req -new -x509 -days 3650 -nodes \
  -out ca-client.crt -keyout ca-client.key -subj "/CN=root-client-ca"

openssl req -new -nodes -text -out client.csr \
  -keyout client.key -subj "/CN=postgres"

openssl x509 -req -in client.csr -text -days 365 \
  -CA ca-client.crt -CAkey ca-client.key -CAcreateserial -out client.crt
```

prepare in `$PGDATA`

```bash
cp ca-client.crt $PGDATA/.
echo -e "\nssl_ca_file = 'ca-client.crt'" >> $PGDATA/postgresql.conf
```

and restart

### test connection

Before connection, remember to set `pg_hba.conf` to only authorized with cetification.

```bash
hostssl    all             all             127.0.0.1/32          cert
```

```bash
psql "sslrootcert=ca.crt sslcert=client.crt sslkey=client.key \
  host=127.0.0.1 dbname=postgres user=postgres sslmode=verify-full"
```