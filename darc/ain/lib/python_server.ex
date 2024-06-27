defmodule Ain.PythonServer do
  use GenServer
  alias Ain.Python

  def start_link(env) do
    GenServer.start_link(__MODULE__, env)
  end

  def init(env) do
    # 启动一个 Python 解释器的实例 并记录其 PID
    python_session = Python.start(env)
    # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
    Python.call(python_session, env, :register_handler, [self()])
    {:ok, python_session}
  end

  def compute(input, method \\ :async) do
    # 计算环境为空
    {:ok, pid} = start_link(nil)
    case method do
      :async ->
        GenServer.cast(pid, {:compute, input})
      :sync ->
        GenServer.call(pid, {:compute, input}, :infinity)
    end
  end

  def handle_call({:compute, input}, _from, session) do
    result = Python.call(session, :test, :compute, [input])
    {:reply, result, session}
  end

  def handle_cast({:compute, input}, session) do
    Python.cast(session, input)
    {:noreply, session}
  end

  def handle_info({:python, message}, session) do
    IO.puts("Received message from python: #{inspect message}")

    # Stop Elixir process
    {:stop, :normal, session}
  end

  def terminate(_reason, session) do
    Python.stop(session)
    :ok
  end
end
