gcc -m32 -o test test.c
i=1
while [ $i -le 300000 ] 
do
    ./test
    i=`expr $i + 1`
done
