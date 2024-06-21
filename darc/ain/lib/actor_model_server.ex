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

  def send(from_name, to_name) do
    from_pid = String.to_atom(from_name)
    {:ok, state} = GenServer.call(from_pid, :get_state)
    message = compute(state.logs)
    GenServer.cast(String.to_atom(to_name), {:receive, message})
  end

  # 发送当前节点的日志中的一个随机条目到另一个指定节点
  def send(target_name, state) do
    message = compute(state.logs)
    GenServer.cast(String.to_atom(target_name), {:receive, message})
  end

  # 从其他节点接收日志并打印
  def handle_cast({:receive, message}, state) do
    updated_state = update_state(state, :logs, fn logs -> [message | logs] end)
    IO.puts("Received message from another node: #{message}")
    {:noreply, updated_state}
  end

  def handle_call({:receive, message}, state) do
    updated_state = update_state(state, :logs, fn logs -> [message | logs] end)
    IO.puts("Received message from another node: #{message}")
    {:noreply, updated_state}
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
