import time
import threading
import struct

from exceptions import StreamBrokenError
import const
from logger import logger

NETWORK_LOOP_SLEEP = 0.001
ENDIAN = 'big'

class ConnectionHandler:
    def __init__(self, socket, player):
        self._socket = socket
        self._player = player
    
    def _decode_header(self):
        """Request Base
            Name 	Size (bytes) 	Description
            opcode 	1 	The operation code to perform, A list of operations currently supported (and their data) can be found in the Operations chapter
            request_id 	4 	The ID for the current request, Used to distinguish responses in the current connection
            
            let opcode_byte: u8 = src[0];
            let opcode: JobOpcode = opcode_byte.into();
            let request_id: u32 = u32::from_be_bytes(src[1..5].try_into().unwrap());"""

        data = self._recvall(5)
        opcode = data[0]
        request_id = int.from_bytes(data[1:5], byteorder=ENDIAN)
        return opcode, request_id
    
    def runner(self):
        """ Todo: we should handle everything asynchronously
         Why the hell in the header is not the length of the packet? and it depends on the opcode?
        """
        try:
            while True:
                opcode, request_id = self._decode_header()

                logger.debug(f"Received opcode: {opcode} request_id: {request_id}")

                if opcode == const.OPCODE_FORCE_UPDATE:
                    self._opcode_force_update(opcode, request_id)
                elif opcode == const.OPCODE_DECRYPT_N_SIGNATURE:
                    self._opcode_decrypt_nsig(opcode, request_id)
                elif opcode == const.OPCODE_DECRYPT_SIGNATURE:
                    self._opcode_decrypt_sig(opcode, request_id)
                elif opcode == const.OPCODE_GET_SIGNATURE_TIMESTAMP:
                    self._opcode_signature_timestamp(opcode, request_id)
                elif opcode == const.OPCODE_PLAYER_STATUS:
                    self._opcode_player_status(opcode, request_id)
                elif opcode == const.OPCODE_PLAYER_UPDATE_TIMESTAMP:
                    self._opcode_player_update_timestamp(opcode, request_id)
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.exception(e)
            self._socket.close()

    def _send_response_packet(self, request_id, data):
        response_packet = request_id.to_bytes(4, byteorder=ENDIAN)
        length = len(data)
        response_packet += length.to_bytes(4, byteorder=ENDIAN)
        response_packet += data

        self._socket.sendall(response_packet)
            
    def _opcode_force_update(self, opcode, request_id):
        """ just ignore the opcode, we update player when we want to """
        status = const.PLAYER_UPDATE_NOT_NEED
        data = struct.pack('!H', status)
        self._send_response_packet(request_id, data)

    def _opcode_player_update_timestamp(self, opcode, request_id):
        player_update_timestamp = self._player.get_player_update_timestamp()
        # 8 bytes
        data = struct.pack('!Q', player_update_timestamp)
        self._send_response_packet(request_id, data)

    def _opcode_player_status(self, opcode, request_id):
        """ Name 	Size (bytes) 	Description
            has_player 	1 	If the server has a player, this variable will be 0xFF. or else, it will be 0x00
            player_id 	4 	The server's current player ID. If the server has no player, this will always be 0x00000000"""

        player_id = self._player.get_player_id()
        data = struct.pack('!B', 0xFF)
        data += struct.pack('!I', player_id)
        self._send_response_packet(request_id, data)

    def _opcode_signature_timestamp(self, opcode, request_id):
        """ Name 	Size (bytes) 	Description
            timestamp 	8 	The signature timestamp from the server's current player"""""
        signature_timestamp = self._player.get_signature_timestamp()
        data = struct.pack('!Q', signature_timestamp)
        self._send_response_packet(request_id, data)

    def _opcode_decrypt_nsig(self, opcode, request_id):
        """Request
            Name 	Size (bytes) 	Description
            size 	2 	The size of the encrypted signature
            string 	size 	The encrypted signature

            Response
            Name 	Size (bytes) 	Description
            size 	2 	The size of the decrypted signature, 0x0000 if an error occurred
            string 	size 	The decrypted signature"""
        
        # read the size of the encrypted signature
        data = self._recvall(2)
        size = int.from_bytes(data, byteorder=ENDIAN)

        # read the encrypted signature
        data = self._recvall(size)
        # decrypt the signature
        decrypted_signature = self._player.decode_nsig(data.decode('utf-8'))
        # convert to bytes
        decrypted_signature = decrypted_signature.encode('utf-8')

        # send the response
        data = struct.pack('!H', len(decrypted_signature))
        data += decrypted_signature
        self._send_response_packet(request_id, data)

    def _opcode_decrypt_sig(self, opcode, request_id):
        """Request
            Name 	Size (bytes) 	Description
            size 	2 	The size of the encrypted signature
            string 	size 	The encrypted signature

            Response
            Name 	Size (bytes) 	Description
            size 	2 	The size of the decrypted signature, 0x0000 if an error occurred
            string 	size 	The decrypted signature"""
        
        # read the size of the encrypted signature
        data = self._recvall(2)
        size = int.from_bytes(data, byteorder=ENDIAN)

        # read the encrypted signature
        data = self._recvall(size)
        # decrypt the signature
        decrypted_signature = self._player.decode_sig(data.decode('utf-8'))
        # convert to bytes
        decrypted_signature = decrypted_signature.encode('utf-8')

        # send the response
        data = struct.pack('!H', len(decrypted_signature))
        data += decrypted_signature
        self._send_response_packet(request_id, data)

    def _recvall(self, size):
        data = b""
        while True:
            chunk = self._socket.recv(size - len(data))
            if not chunk:
                raise StreamBrokenError("Stream broken.")
            data += chunk
            if len(data) == size:
                return data
            # we are using a blocking socket, so we should not sleep
            assert(len(data) < size)
