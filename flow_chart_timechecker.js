st29=>start: start timechecker(input: times)
cond35=>condition: while True
op86=>operation: check current time
cond89=>condition: if opening <= current time <= hotclosing
op93=>operation: sleep delay_hot
cond104=>condition: if hotclosing <= current time <= closing
op108=>operation: sleep delay_nor
op123=>operation: sleep delay_off
e134=>end: end timechecker
st29->cond35
cond35(yes)->op86
op86->cond89
cond89(yes)->op93
op93->e134
cond89(no)->cond104
cond104(yes)->op108
op108->e134
cond104(no)->op123
op123(right)->op86
cond35(no)->e134