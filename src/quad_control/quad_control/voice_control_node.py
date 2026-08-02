import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import speech_recognition as sr
import threading

SPEED = 0.4

COMMAND_MAP = {
    'forward':  (SPEED, 0, 0),
    'backward': (-SPEED, 0, 0),
    'back':     (-SPEED, 0, 0),
    'left':     (0, SPEED, 0),
    'right':    (0, -SPEED, 0),
    'up':       (0, 0, SPEED),
    'down':     (0, 0, -SPEED),
    'stop':     (0, 0, 0),
}

class VoiceControl(Node):
    def __init__(self):
        super().__init__('voice_control_node')
        self.pub = self.create_publisher(Twist, '/cmd_vel_voice', 10)
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        threading.Thread(target=self.listen_loop, daemon=True).start()
        self.get_logger().info('Voice control listening... say "forward", "stop", etc.')

    def listen_loop(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while rclpy.ok():
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio).lower()
                    self.get_logger().info(f'Heard: {text}')
                    self.handle_command(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.get_logger().warn(f'Speech API error: {e}')

    def handle_command(self, text):
        for keyword, (vx, vy, vz) in COMMAND_MAP.items():
            if keyword in text:
                msg = Twist()
                msg.linear.x, msg.linear.y, msg.linear.z = float(vx), float(vy), float(vz)
                self.pub.publish(msg)
                return

def main():
    rclpy.init()
    node = VoiceControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()