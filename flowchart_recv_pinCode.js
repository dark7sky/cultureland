st138=>start: start recv_pinCode(input: Tbot, times)
op145=>operation: get telegram messages 
io146=>inputoutput: save as previous messages
cond150=>condition: while (not abort)
op159=>operation: get telegram messages 
cond160=>condition: Any new pin code message?
op161=>operation: set active_count
st162=>start: function timechecker
cond163=>condition: active_count > 0 ?
op164=>operation: sleep 2s
op165=>operation: received pin code
op167=>operation: Edit telegram message (running)
op169=>operation: Delete received pin code telegram message
e172=>end: return result, msg_id
st138->op145
op145->io146
io146->cond150
cond150(yes)->op159
op159->cond160
cond160(yes)->op161
op161->op165
cond160(no)->cond163
cond163(no)->st162
cond163(yes)->op164
op164(right)->op159
st162(right)->op159
cond150(no)->op165
op165->op167
op167->op169
op169->e172

