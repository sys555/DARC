defmodule Ain.ActorModelServer do
  use GenServer

  # 启动 GenServer，使用 init 字段作为名称注册
  def start_link(args) do
    name = String.to_atom(args["init"])  # 将 init 字段转换为原子作为名称
    GenServer.start_link(__MODULE__, args, name: name)
  end

  # 初始化
  def init(args) do
    state = %{
      init: args["init"],
      env: args["env"],
      logs: args["logs"]
    }
    {:ok, state}
  end

  def send(from_name, to_name, message) do
    from_pid = String.to_atom(from_name)
    to_pid = String.to_atom(to_name)
    GenServer.cast(to_pid, {:receive, message, from_pid})
  end

  # # 发送当前节点的日志中的一个随机条目到另一个指定节点
  # def send(target_name, state) do
  #   message = compute(state.logs)
  #   GenServer.cast(String.to_atom(target_name), {:receive, message})
  # end

  def handle_cast({:receive, message, from_pid}, state) do
    updated_state = update_state(state, :logs, fn logs -> [message | logs] end)
    IO.puts("Received message from another node: #{message}")
    # 生成响应消息并发送回发送者
    response_message = compute(state.logs)
    GenServer.cast(from_pid, {:receive, response_message, self()})
    {:noreply, updated_state}
  end

  # 如果需要处理同步消息，也应更新此逻辑
  def handle_call({:receive, message, from_pid}, _from, state) do
    updated_state = update_state(state, :logs, fn logs -> [message | logs] end)
    IO.puts("Received message from another node: #{message}")
    # 生成响应消息并发送回发送者
    response_message = compute(state.logs)
    GenServer.cast(from_pid, {:receive, response_message, self()})
    {:reply, :ok, updated_state}
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
