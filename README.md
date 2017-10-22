Chat Events

Format:
/<trigger-event>
     <{event data}>
     /<response-event>
        <{response-data}>

/test 
    /test_back
        { data: 'test run' }

# room-id should be mentor + mentee
/join
    { mentor: <mentor-id>, mentee: <mentee-id> }
    /joined
        { data: ['chat history'] }


/leave
    { room: <room-id> }
    /left
        {  data: 'leaving room' }

/send_msg
    { data: <messsage>, mentor: <mentor-id>, mentee: <mentee-id>, _id: <mentee-id|mentor-id>  }
    /msg_sent
        { data: <message>, isMentor: <true|false>, mentorOnly: <true|false> }

/disconnect
    /disconnected
        { data: disconnected }


