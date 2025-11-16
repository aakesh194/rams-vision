import socket, cv2, pickle, struct

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 8000))
server_socket.listen(1)
conn, addr = server_socket.accept()

data = b""
payload_size = struct.calcsize(">L")
while True:
    while len(data) < payload_size:
        data += conn.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)

    cv2.imshow("Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
