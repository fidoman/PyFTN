#!/bin/env python3 -bb

""" listen for incoming connection:
    processes received files 
    and generates outbound files on request

    Outbound:
    on session mailer establishes connection to daemon and send request:
    GET NETMAIL FOR address
    GET ECHOMAIL FOR address
    GET FILES FOR address
    GET ALL FOR address
    daemon answers
    QUEUE EMPTY
    if there is no outbound
    or
    FILE filename LENGTH length
    then sends binary file content
    after receiving file mailer transfers it and sends
    OK
    then demons commits export and sends next file or signals that queue empty
    if no OK is received exported data is not get removed
    from database and will be sent again

    Inbound:
    > FILE file FROM address LENGTH length
    > (data)
    < OK
    then repeat or close connection if done or go to outbound processing
