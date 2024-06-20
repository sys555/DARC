defmodule Ain.ActorModelServer do
  use GenServer

  # 启动 GenServer
  def start_link(args) do
    GenServer.start_link(__MODULE__, args)
  end

  # 初始化
  def init(args) do
    state = %{init: args["init"], env: args["env"], logs: args["logs"]}
    {:ok, state}
  end

  # 打印日志消息
  def print_logs(pid) do
    GenServer.call(pid, :print_logs)
  end

  # 处理调用
  def handle_call(:print_logs, _from, state) do
    Enum.each(state.logs, &IO.puts/1)
    {:reply, :ok, state}
  end
end
