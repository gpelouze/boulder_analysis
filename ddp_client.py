#!/usr/bin/env python3

import ejson
import websocket

class DDPClient(websocket.WebSocketApp):
    def __init__(self, url, header=None,
                 on_open=None, on_message=None, on_error=None,
                 on_close=None, on_ping=None, on_pong=None,
                 on_cont_message=None,
                 keep_running=True, get_mask_key=None, cookie=None,
                 subprotocols=None,
                 on_data=None):
        """
        url: websocket url.
        header: custom header for websocket handshake.
        keep_running: this parameter is obsolete and ignored.
        get_mask_key: a callable to produce new mask keys,
          see the WebSocket.set_mask_key's docstring for more information
        subprotocols: array of available sub protocols. default is None.
        """
        self.url = url
        self.header = header if header is not None else []
        self.cookie = cookie

        self.keep_running = False
        self.get_mask_key = get_mask_key
        self.sock = None
        self.last_ping_tm = 0
        self.last_pong_tm = 0
        self.subprotocols = subprotocols

        self.collections = {}

        self._request_id = 0

    def _next_id(self):
        self._request_id += 1
        return str(self._request_id)

    def send(self, data):
        super().send(ejson.dumps(data))

    # client -> server messages -----------------------------------------------

    def connect(self):
        self.send({'msg': 'connect', 'version': 'pre1', 'support': ['pre1']})

    def sub(self, name, params):
        id_ = self._next_id()
        self.send({'msg': 'sub', 'id': id_,
                   'name': name, 'params': params})
        return id_

    def unsub(self):
        self.send({'msg': 'unsub', 'id': self._next_id()})

    def method(self, method, params=[]):
        self.send({'msg': 'method', 'id': self._next_id(),
                   'method': method, 'params': params})


    # server -> client messages callbacks -------------------------------------

    def on_added(self, collection, id_, fields):
        if collection not in self.collections:
            self.collections[collection] = {}
        self.collections[collection][id_] = fields

    def on_changed(self, collection, id_, fields, cleared):
        document = self.collections[collection][id_]
        document.update(fields)
        for key in cleared:
            del document[key]

    def on_removed(self, collection, id_):
        del self.collections[collection][id_]

    def on_ready(self, subs):
        pass

    def on_result(self, id_, error, result):
        pass

    def on_updated(self, methods):
        pass

    # websocket callbacks -----------------------------------------------------

    def on_open(self):
        self.connect()

    def on_message(self, msg):
        msg = ejson.loads(msg)

        if msg.get('msg') == 'added':
            self.on_added(msg['collection'], msg['id'], msg.get('fields', {}))

        if msg.get('msg') == 'changed':
            self.on_changed(msg['collection'], msg['id'],
                            msg.get('fields', {}), msg.get('cleared', []))

        if msg.get('msg') == 'removed':
            self.on_removed(msg['collection'], msg['id'])

        if msg.get('msg') == 'ready':
            self.on_ready(msg['subs'])

        if msg.get('msg') == 'addedBefore':
            raise NotImplementedError

        if msg.get('msg') == 'movedBefore':
            raise NotImplementedError


        if msg.get('msg') == 'result':
            self.on_result(msg['id'], msg.get('error'), msg.get('result', {}))

        if msg.get('msg') == 'updated':
            self.on_updated(msg['methods'])


        return msg

    def on_data(self, data, type_, continued):
        pass
    def on_cont_message(self, data, continued):
        pass
    def on_error(self, error):
        pass
    def on_close(self):
        pass
    def on_ping(self):
        pass
    def on_pong(self):
        pass
