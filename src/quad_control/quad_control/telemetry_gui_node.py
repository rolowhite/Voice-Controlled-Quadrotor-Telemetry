import sys
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                              QPushButton, QGridLayout, QVBoxLayout)
from PyQt5.QtCore import QTimer

SPEED = 0.4

def quaternion_to_euler(x, y, z, w):
    """Returns roll, pitch, yaw in degrees."""
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y * y)
    roll = math.degrees(math.atan2(t0, t1))

    t2 = 2.0 * (w * y - z * x)
    t2 = max(-1.0, min(1.0, t2))
    pitch = math.degrees(math.asin(t2))

    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.degrees(math.atan2(t3, t4))
    return roll, pitch, yaw


class TelemetryNode(Node):
    """Pure ROS2 side: publishers/subscribers only, no Qt code here."""
    def __init__(self):
        super().__init__('telemetry_gui_node')
        self.pub_manual = self.create_publisher(Twist, '/cmd_vel_manual', 10)
        self.pub_mode = self.create_publisher(String, '/control_mode', 10)
        self.create_subscription(Odometry, '/model/quadrotor/odometry', self.odom_cb, 10)
        self.latest = {'pos': (0, 0, 0), 'rpy': (0, 0, 0),
                        'vel': (0, 0, 0), 'status': 'NO DATA'}

    def odom_cb(self, msg: Odometry):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        self.latest['pos'] = (p.x, p.y, p.z)
        self.latest['rpy'] = quaternion_to_euler(q.x, q.y, q.z, q.w)
        self.latest['vel'] = (v.x, v.y, v.z)
        self.latest['status'] = 'ARMED / RECEIVING'

    def send_manual(self, vx, vy, vz):
        msg = Twist()
        msg.linear.x, msg.linear.y, msg.linear.z = float(vx), float(vy), float(vz)
        self.pub_manual.publish(msg)

    def set_mode(self, mode: str):
        self.pub_mode.publish(String(data=mode))


class MainWindow(QMainWindow):
    def __init__(self, ros_node: TelemetryNode):
        super().__init__()
        self.ros_node = ros_node
        self.setWindowTitle('Quadrotor Telemetry & Control')
        self.mode = 'manual'

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        # --- Telemetry labels ---
        self.lbl_pos = QLabel('Position: --')
        self.lbl_rpy = QLabel('Orientation: --')
        self.lbl_vel = QLabel('Velocity: --')
        self.lbl_status = QLabel('Status: --')
        for lbl in (self.lbl_pos, self.lbl_rpy, self.lbl_vel, self.lbl_status):
            lbl.setStyleSheet('font-size: 14px; padding: 2px;')
            outer.addWidget(lbl)

        # --- Mode toggle ---
        self.btn_mode = QPushButton('Mode: MANUAL (click to switch to VOICE)')
        self.btn_mode.clicked.connect(self.toggle_mode)
        outer.addWidget(self.btn_mode)

        # --- Manual control grid ---
        grid = QGridLayout()
        outer.addLayout(grid)

        def mkbtn(label, vx, vy, vz, row, col):
            b = QPushButton(label)
            b.clicked.connect(lambda: self.ros_node.send_manual(vx, vy, vz))
            grid.addWidget(b, row, col)
            return b

        mkbtn('Forward',  SPEED, 0, 0,      0, 1)
        mkbtn('Left',     0, SPEED, 0,      1, 0)
        mkbtn('Stop',     0, 0, 0,          1, 1)
        mkbtn('Right',    0, -SPEED, 0,     1, 2)
        mkbtn('Backward', -SPEED, 0, 0,     2, 1)
        mkbtn('Up',       0, 0, SPEED,      0, 3)
        mkbtn('Down',     0, 0, -SPEED,     1, 3)

        # --- Timer: pump the ROS 2 executor AND refresh labels ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(50)  # 20 Hz

    def toggle_mode(self):
        self.mode = 'voice' if self.mode == 'manual' else 'manual'
        self.ros_node.set_mode(self.mode)
        self.btn_mode.setText(
            f'Mode: {self.mode.upper()} (click to switch to '
            f'{"MANUAL" if self.mode == "voice" else "VOICE"})')

    def tick(self):
        rclpy.spin_once(self.ros_node, timeout_sec=0)
        d = self.ros_node.latest
        self.lbl_pos.setText('Position (x,y,z): %.2f, %.2f, %.2f' % d['pos'])
        self.lbl_rpy.setText('Orientation R/P/Y (deg): %.1f, %.1f, %.1f' % d['rpy'])
        self.lbl_vel.setText('Velocity (x,y,z): %.2f, %.2f, %.2f' % d['vel'])
        self.lbl_status.setText(f'Status: {d["status"]} | Active mode: {self.mode.upper()}')


def main():
    rclpy.init()
    ros_node = TelemetryNode()
    app = QApplication(sys.argv)
    win = MainWindow(ros_node)
    win.resize(420, 320)
    win.show()
    app.exec_()
    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()