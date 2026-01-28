const DEV_PORTS = new Set(["3000", "8081", "19006"]);

const resolveBackendPort = (port: string) => {
  const isVitePort = !!port && /^517\d$/.test(port);
  const isDevPort = DEV_PORTS.has(port);
  if (!port) {
    return "8000";
  }
  if (isVitePort || isDevPort) {
    return "8000";
  }
  return port;
};

const resolveHost = (hostname: string) => (hostname === "0.0.0.0" ? "localhost" : hostname);

export const getBackendBaseUrl = () => {
  const { protocol, hostname, port } = window.location;
  return `${protocol}//${resolveHost(hostname)}:${resolveBackendPort(port)}`;
};

export const getBackendWsBaseUrl = () => {
  const { protocol, hostname, port } = window.location;
  const wsProtocol = protocol === "https:" ? "wss" : "ws";
  return `${wsProtocol}://${resolveHost(hostname)}:${resolveBackendPort(port)}`;
};
