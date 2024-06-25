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

  # 发送消息
  def send(from_name, to_name, message_type, message) do
    from_pid = String.to_atom(from_name)
    to_pid = String.to_atom(to_name)
    GenServer.cast(to_pid, {:receive, message, from_pid, message_type})
  end

  # 处理接收到的消息
  def handle_cast({:receive, message, from_pid, :initial}, state) do
    IO.puts("#{state.init} received initial message: #{message}")
    updated_state = update_state(state, :logs, fn logs -> [message | logs] end)
    # 发送ACK消息
    response_message = compute(state.logs)
    GenServer.cast(from_pid, {:receive, response_message, self(), :ack})
    {:noreply, updated_state}
  end

  def handle_cast({:receive, message, from_pid, :ack}, state) do
    IO.puts("#{state.init} received ACK: #{message}")
    # 发送FINAL消息
    final_message = "FINAL"
    GenServer.cast(from_pid, {:receive, final_message, self(), :final})
    {:noreply, state}
  end

  def handle_cast({:receive, message, from_pid, :final}, state) do
    IO.puts("#{state.init} received FINAL message: #{message}, communication ended.")
    {:noreply, state}
  end

  # 构造消息，选择日志中的一个随机条目
  def compute(logs) do
    Enum.random(logs)
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

  def handle_call(:get_state, _from, state) do
    {:reply, {:ok, state}, state}
  end

  # 更新状态的通用函数
  defp update_state(state, key, func) do
    Map.update!(state, key, func)
  end
end
