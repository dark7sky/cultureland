st3=>start: start main
op10=>operation: telegram bot setting
op12=>operation: telegram send ready Msg
cond15=>condition: while True
st144=>start: function recv_pinCode
op151=>operation: set_chrome_driver if not
cond154=>condition: setting chrome driver failed?
op158=>operation: telegram send chrome error Msg
op172=>operation: go to login page
op174=>operation: load_cookies
cond179=>condition: not cultureland checkLoginStatus
op199=>operation: trial_count += 1
op201=>operation: cultureland_doLogin
cond204=>condition: if trial_count > 10
op216=>operation: save_cookies
op218=>operation: chargePinCode
cond221=>condition: charge process failed?
op225=>operation: telegram send error Msg
op254=>operation: save_cookies
cond257=>condition: if active_count = 0
op261=>operation: terminate webdriver

op229=>operation: check account balance
cond238=>condition: check charge status
op242=>operation: Telegram delete running message
op244=>operation: Telegram send complete message
op248=>operation: Telegram delete running message
op250=>operation: Telegram send failed message
e270=>end: end main

st3->op10
op10->op12
op12->cond15
cond15(yes)->st144
st144->op151
op151->cond154
cond154(yes,right)->op158
op158->e270
cond154(no)->op172
op172->op174
op174->cond179
cond179(yes,right)->op199
op199->op201
op201->cond204
cond204(no,left)->cond179
cond204(yes,right)->e270
cond179(no)->op216
op216->op218
op218->cond221
cond221(yes,right)->op225
op225->op254
op254->cond257
cond257(yes)->op261
op261(right)->cond15
cond257(no)->cond15
cond221(no)->op229
op229->cond238
cond238(yes)->op242
op242->op244
op244(right)->cond15
cond238(no)->op248
op248->op250
op250(right)->cond15