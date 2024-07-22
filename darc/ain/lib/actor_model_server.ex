defmodule Ain.ActorModelServer do
  use GenServer
  alias Ain.Python
  # 启动 GenServer，使用 init 字段作为名称注册
  def start_link(args) do
    name = String.to_atom(args["init"])  # 将 init 字段转换为原子作为名称
    GenServer.start_link(__MODULE__, args, name: name)
  end

  def init(args) do
    IO.inspect(args)
    try do
      python_session =
        if args["env"] == "Graph" do
          # Graph env 不加载 python 解释器
          nil
        else
          # 启动一个 Python 解释器的实例 并记录其 PID
          session = Python.start(args["env"])
          # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
          Python.call(session, String.to_atom(args["env"]), :register_handler, [self()])
          session
        end

      state = %{
        init: args["init"],
        env: args["env"],
        logs: args["logs"],
        python_session: python_session,
        # graph contract pid
        callback_pid: nil
      }
      {:ok, state}
    rescue
      e in UndefinedFunctionError ->
        IO.puts("An error occurred: #{inspect(e)}")
        {:stop, e}
    end
  end

  # 发送消息
  def send(from_name, to_name, message_type, message) do
    from_pid = String.to_atom(from_name)
    to_pid = String.to_atom(to_name)
    GenServer.cast(to_pid, {:receive, message, from_pid, message_type})
  end

  # 处理接收到的消息
  def handle_cast({:receive, message, from_pid, :initial}, state) do
    updated_state = update_state(state, :logs, fn logs -> [message | logs] end)
    # MAS 回调绑定
    updated_state = %{state | callback_pid: from_pid}
    # 发送ACK消息
    if state.env == "Graph" do
      graph_compute(updated_state, message)
    else
      response_message = compute(state, message)
      GenServer.cast(from_pid, {:receive, response_message, self(), :ack})
    end
    {:noreply, updated_state}
  end

  def handle_cast({:receive, message, from_pid, :ack}, state) do
    # IO.puts("#{state.init} received ACK: #{message}")
    # 发送FINAL消息
    final_message = "FINAL"
    GenServer.cast(from_pid, {:receive, final_message, self(), :final})
    {:noreply, state}
  end

  def handle_cast({:receive, message, from_pid, :final}, state) do
    # IO.puts("#{state.init} received FINAL message: #{message}, communication ended.")
    {:noreply, state}
  end

  def handle_cast({:all_logs_received, updated_logs}, state) do
    response_message = updated_logs
    GenServer.cast(state.callback_pid, {:receive, response_message, self(), :ack})
    {:noreply, state}
  end

  def compute(state, input) do
    python_call_res = Python.call(state.python_session, String.to_atom(state.env), :compute, [input])
    # 当传输或打印一个包含非 ASCII 字符的字符列表时，每个字符会被其对应的 Unicode 码点表示，必须做list to str
    res = List.to_string(python_call_res)
  end

  defp graph_compute(state, input) do
    uid = state.init
    # create a MAS
    pid = GraphContract.start_with_graph_id_and_init_data(uid, input, self())
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
