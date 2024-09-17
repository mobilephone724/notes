---
title: "Build PostgreSQL From Source"
date: 2024-04-16T23:09:39+08:00
---


## Download through git

See [official docs](https://www.postgresql.org/docs/current/git.html) for detail. Below is a simple example:

```bash
export user=dev
export src_dir=postgresql

export build_dir=/home/${user}/build
export data_dir=/home/${user}/data

export superuser=postgres
export defaultdb=test

${build_dir}/bin/pg_ctl -D ${data_dir} stop
rm -rf ${build_dir}
rm -rf ${data}

cd ~ #start from home/${user}
git clone https://git.postgresql.org/git/postgresql.git
cd ${src_dir}
git clean -xdf # may be too dangerous

# delete for add some configures accordingly
./configure \
    --prefix=${build_dir} \
    --enable-cassert \
    --with-tcl \
    --with-perl \
    --with-python \
    --enable-debug \
    --without-icu \
    --with-openssl \
    CC=/usr/bin/gcc \
    CFLAGS='-O0 -pipe -Wall -g3'

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

‍