defmodule Ain.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # 启动 Ecto 存储库
      DB.Repo,
      MasrpcServerState,
      {GRPC.Server.Supervisor, endpoint: Masrpc.Endpoint, port: 50051, start_server: true},
    ]

    # 定义监督策略
    opts = [strategy: :one_for_one, name: Ain.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
