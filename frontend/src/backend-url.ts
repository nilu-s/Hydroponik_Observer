const resolveBackendPort = (port: string) => {
  const isVitePort = !!port && /^517\d$/.test(port);
  return port ? (isVitePort ? "8000" : port) : "8000";
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
