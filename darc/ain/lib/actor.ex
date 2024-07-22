defmodule Ain.Actor do
  use GenServer

  def start_link(args) do
    GenServer.start_link(__MODULE__, args, uid: args["uid"])
  end

  def init(args) do
    try do
      # 启动一个 Python 解释器的实例 并记录其 PID
      python_session = Python.start(args["env"])
      # 将 当前 GenServer 进程注册为 Python 代码中异步操作的回调处理器
      Python.call(python_session, String.to_atom(args["env"]), :register_handler, [self()])
      state = %{
        uid: "",
        name: "",
        role: "",
        # uid: content
        input_cache: %{},
        compute_result: [],
        # uid: message
        output_cache: %{},
        prefix: [],
        # uid: pid
        next: %{},
      }
    rescue
      e in UndefinedFunctionError ->
        IO.puts("An error occurred: #{inspect(e)}")
        {:stop, e}
    end
  end

end
