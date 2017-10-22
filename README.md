#Chat Events

* **Format**:
```
/<trigger-event>
     <{event data}>
     /<response-event>
        <{response data}>
```


* **Test End Point**
```
/test 
    /test_back
        { data: 'test run' }

```

* **API End Points**

```
/join
    { mentor: <mentor-id>, mentee: <mentee-id> }
    /joined
        { data: ['chat history'] }
```

```
/leave
    { mentor: <mentor-id>, mentee: <mentee-id> }
    /left
        {  data: 'leaving room' }
```

```
/send_msg
    { data: <messsage>, mentor: <mentor-id>, mentee: <mentee-id>, _id: <sender-id>, lang: <prefered-lang>  }
    /msg_sent
        { data: <message>, _id: <sender-id> }
```

```
/disconnect
    { mentor: <mentor-id>, mentee: <mentee-id>  }
    /disconnected
        { data: disconnected }
```

