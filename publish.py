import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from sense_hat import SenseHat
from time import sleep

sense = SenseHat()
sense.clear()
ball_position = [4,4]
ball_velocity = [-1,1]
bat_y = 4
white = (255, 255, 255)
print("Done")

MQTT_SERVER = "test.mosquitto.org"
MQTT_PATH = "Pi2_channel"
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)
    
def draw_bat():
    sense.set_pixel(7, bat_y, white)
    sense.set_pixel(7, bat_y-1, white)
    sense.set_pixel(7, bat_y+1, white)
        
def move_up(event):
    global bat_y
    if event.action =='pressed' and bat_y > 1:
        bat_y -= 1
        
def move_down(event):
    global bat_y
    if event.action == 'pressed' and bat_y < 6:
        bat_y += 1
        
def draw_ball():
    #global score
    global ball_velocity
    global ball_position
    ball_colour = (0, 255, 0)
    delay = 0.35
    while ball_velocity[0] == 1 or ball_position[0] >= 0:# oposite velo[0] == -1 and pos[0] < 0
        draw_bat()
        sense.stick.direction_up = move_up
        sense.stick.direction_down = move_down
        sense.set_pixel(ball_position[0], ball_position[1], ball_colour)
        ball_position[0] += ball_velocity[0]
        ball_position[1] += ball_velocity[1]
            # when the ball is hit
        if ball_position[0] == 7:
            publish.single("Pi1_channel", "win", hostname='test.mosquitto.org' )
            while True:
                sense.show_message("Lose")
        if ball_position[1] == 7 or ball_position[1] == 0:
            ball_velocity[1] = -ball_velocity[1]
        
        sleep(delay)
        sense.clear()
            # bat hit ball
        if ball_position[0] == 6 and (bat_y-1 <= ball_position[1] <= bat_y+1):
            ball_velocity[0] = -ball_velocity[0]
          
    # The callback for when afPUBLISH message is received from the server.
    msg = [7, ball_position[1], -1, ball_velocity[1]]
    msg = ",".join(str(i) for i in msg)
    publish.single("Pi1_channel", bytes(msg, 'utf-8'), hostname='test.mosquitto.org' )

def on_message(client, userdata, msg):
    global ball_velocity
    global ball_position
    print(msg.topic+" "+str(msg.payload))
    if str(msg.payload) == "b'win'":
        while True:
            sense.show_message("Win")
    msg = msg.payload.decode("utf-8").split(",")
    msg = [int(i) for i in msg]
    ball_position = [msg[0], msg[1]]
    ball_velocity = [msg[2], msg[3]]
    draw_ball()
    # more callbacks, etc


client = mqtt.Client()
draw_ball()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()