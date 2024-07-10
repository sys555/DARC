defmodule Ain.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # 启动 Ecto 存储库
      DB.Repo,
    ]

    # 定义监督策略
    opts = [strategy: :one_for_one, name: Ain.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
