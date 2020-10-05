import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from sense_hat import SenseHat
from time import sleep

sense = SenseHat()
sense.clear()
bat_y = 4
white = (255, 255, 255)
print("Done")

MQTT_SERVER = "test.mosquitto.org"
MQTT_PATH = "Pi1_channel"
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

def draw_bat():
    sense.set_pixel(0, bat_y, white)
    sense.set_pixel(0, bat_y-1, white)
    sense.set_pixel(0, bat_y+1, white)
    
def move_up(event):
    global bat_y
    if event.action == 'pressed' and bat_y > 1:
        bat_y -=1
    
def move_down(event):
    global bat_y
    if event.action == 'pressed' and bat_y < 6:
        bat_y +=1
        

def draw_ball():
    #global score
	global ball_velocity
	global ball_position
	ball_colour = (0, 255, 0)
	delay = 0.35
	while ball_velocity[0] == -1 or ball_position[0] <= 7: # oposite velo[0] == -1 and pos[0] < 0
                draw_bat()
                sense.stick.direction_up = move_up
                sense.stick.direction_down = move_down
                sense.set_pixel(ball_position[0], ball_position[1], ball_colour)
                ball_position[0] += ball_velocity[0]
                ball_position[1] += ball_velocity[1]
            # when the ball is hit
                if ball_position[0] == 0:
                    publish.single("Pi2_channel", "win", hostname='test.mosquitto.org')
                    while True:
                        sense.show_message("GG")
                if ball_position[1] == 7 or ball_position[1] == 0:
                    ball_velocity[1] = -ball_velocity[1]
            # bat hit ball
                if ball_position[0] == 1 and (bat_y-1 <= ball_position[1] <= bat_y+1):
                    ball_velocity[0] = -ball_velocity[0]
                sleep(delay)
                sense.clear()
    # The callback for when a PUBLISH message is received from the server.
	msg = [0, ball_position[1], 1, ball_velocity[1]]
	msg = ",".join(str(i) for i in msg)
	publish.single("Pi2_channel", bytes(msg, 'utf-8'), hostname='test.mosquitto.org' )

def on_message(client, userdata, msg):
        global ball_velocity
        global ball_position
        print(msg.topic+" "+str(msg.payload))
        if str(msg.payload) == "b'win'":
            while True:
                sense.show_message("Win")
        msg = msg.payload.decode("utf-8").split(",")
        msg = [int(i) for i in msg]
        print(msg)
        ball_position = [msg[0], msg[1]]
        ball_velocity = [msg[2], msg[3]]
        draw_bat()
        draw_ball()
        sense.stick.direction_up = move_up
        senes.stick.direction_down = move_down
    # more callbacks, etc


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
