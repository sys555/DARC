defmodule Ain.ActorModelServer do
  use GenServer

  # 启动 GenServer，使用 init 字段作为名称注册
  def start_link(args) do
    name = String.to_atom(args["init"])  # 将 init 字段转换为原子作为名称
    GenServer.start_link(__MODULE__, args, name: name)
  end

  # 初始化
  def init(args) do
    {:ok, python_server_pid} = PythonServer.start_link(args["env"])
    state = %{
      init: args["init"],
      env: args["env"],
      logs: args["logs"],
      python_server_pid: python_server_pid,
    }
    {:ok, state}
  end

  # 发送当前节点的日志到另一个指定节点
  def send_logs_to_other_node(source_name, target_name) do
    # 使用 case 语句来处理所有可能的返回
    case GenServer.call(String.to_atom(source_name), :get_logs) do
      logs when is_list(logs) ->
        GenServer.cast(String.to_atom(target_name), {:receive_logs_from_other, logs})

      {:ok, logs} when is_list(logs) ->
        GenServer.cast(String.to_atom(target_name), {:receive_logs_from_other, logs})

      _ ->
        IO.puts("Failed to retrieve logs from #{source_name}")
    end
  end

  # 从其他节点接收日志并打印
  def handle_cast({:receive_logs_from_other, logs}, state) do
    IO.puts("Received logs from another node:")
    Enum.each(logs, &IO.puts/1)
    {:noreply, state}
  end

  # 获取当前节点的日志
  def handle_call(:get_logs, _from, state) do
    {:reply, state.logs, state}
  end

  # 打印日志消息
  def print_logs(name) do
    GenServer.call(String.to_atom(name), :print_logs)
  end

  # 处理来自其他节点的打印请求
  def handle_call(:print_logs, _from, state) do
    Enum.each(state.logs, &IO.puts/1)
    {:reply, :ok, state}
  end
end
