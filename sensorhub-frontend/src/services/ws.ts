import { getBackendWsBaseUrl } from "./backend-url";
import { WsClientMsg, WsServerMsg } from "../types";

type Status = "connected" | "disconnected" | "connecting";
type MsgHandler = (msg: WsServerMsg) => void;
type StatusHandler = (status: Status) => void;

const BACKOFFS = [1000, 2000, 5000, 10000];

export class LiveWsClient {
  private socket: WebSocket | null = null;
  private onMsg: MsgHandler;
  private onStatus: StatusHandler;
  private reconnectAttempt = 0;
  private subscriptions = new Set<string>();
  private closing = false;

  constructor(onMsg: MsgHandler, onStatus: StatusHandler) {
    this.onMsg = onMsg;
    this.onStatus = onStatus;
  }

  connect() {
    if (this.socket || this.closing) {
      return;
    }
    this.onStatus("connecting");
    this.socket = new WebSocket(`${getBackendWsBaseUrl()}/api/live`);

    this.socket.onopen = () => {
      this.reconnectAttempt = 0;
      this.onStatus("connected");
      this.subscriptions.forEach((setupId) => {
        this.send({ t: "sub", setupId });
      });
    };

    this.socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as WsServerMsg;
        this.onMsg(msg);
      } catch {
        this.onMsg({ t: "error", msg: "invalid ws payload" });
      }
    };

    this.socket.onerror = () => {
      this.socket?.close();
    };

    this.socket.onclose = () => {
      this.socket = null;
      if (!this.closing) {
        this.onStatus("disconnected");
        this.scheduleReconnect();
      }
    };
  }

  close() {
    this.closing = true;
    this.socket?.close();
    this.socket = null;
    this.onStatus("disconnected");
  }

  subscribe(setupId: string) {
    this.subscriptions.add(setupId);
    this.send({ t: "sub", setupId });
  }

  unsubscribe(setupId: string) {
    this.subscriptions.delete(setupId);
    this.send({ t: "unsub", setupId });
  }

  private send(payload: WsClientMsg) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  private scheduleReconnect() {
    const delay = BACKOFFS[Math.min(this.reconnectAttempt, BACKOFFS.length - 1)];
    this.reconnectAttempt += 1;
    setTimeout(() => this.connect(), delay);
  }
}
